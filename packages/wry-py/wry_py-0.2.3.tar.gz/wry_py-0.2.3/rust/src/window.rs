use crate::elements::Element;
use crate::renderer::{render_to_html, render_to_json, render_to_json_partial};
use parking_lot::Mutex;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::sync::Arc;
use wry::WebViewBuilder;
use tao::event_loop::EventLoopProxy;

#[cfg(target_os = "linux")]
use {
    gtk::prelude::*,
    gtk::{Box as GtkBox, Orientation},
    wry::WebViewBuilderExtUnix,
};

#[cfg(not(target_os = "linux"))]
use {
    tao::event::{Event, WindowEvent},
    tao::event_loop::{ControlFlow, EventLoop, EventLoopBuilder},
    tao::window::WindowBuilder,
};

/// Custom events we can send to the event loop
#[derive(Debug, Clone)]
pub enum UserEvent {
    PatchRoot(String),             // JSON content for DOM patching
    PatchElement(String, String),  // (element_id, json) for partial update
    SetTitle(String),
    Close,
}

/// Shared state between Python and the webview
struct WebViewState {
    callbacks: HashMap<String, Py<PyAny>>,
    pending_html: Option<String>,
    pending_title: Option<String>,
    pending_element_updates: Vec<(String, String)>, // (id, json) pairs
    should_close: bool,
}

impl WebViewState {
    fn new() -> Self {
        WebViewState {
            callbacks: HashMap::new(),
            pending_html: None,
            pending_title: None,
            pending_element_updates: Vec::new(),
            should_close: false,
        }
    }
}

/// Main window class exposed to Python
#[pyclass]
pub struct UiWindow {
    title: String,
    width: u32,
    height: u32,
    event_proxy: Arc<Mutex<Option<EventLoopProxy<UserEvent>>>>,
    state: Arc<Mutex<WebViewState>>,
    is_running: Arc<Mutex<bool>>,
    background_color: (u8, u8, u8, u8),
}

#[pymethods]
impl UiWindow {
    /// Create a new window.
    ///
    /// Args:
    ///     title: Window title. Defaults to "Python App".
    ///     width: Window width in pixels. Defaults to 800.
    ///     height: Window height in pixels. Defaults to 600.
    ///     background_color: Background color as hex string (e.g., "#1a1a1a"). Defaults to dark gray.
    #[new]
    #[pyo3(signature = (title = None, width = None, height = None, background_color = None), text_signature = "(title=None, width=None, height=None, background_color=None)")]
    fn new(
        title: Option<String>,
        width: Option<u32>,
        height: Option<u32>,
        background_color: Option<String>,
    ) -> Self {
        let bg = background_color
            .and_then(|c| parse_hex_color(&c))
            .unwrap_or((26, 26, 26, 255)); // Default: #1a1a1a

        UiWindow {
            title: title.unwrap_or_else(|| "Python App".to_string()),
            width: width.unwrap_or(800),
            height: height.unwrap_or(600),
            event_proxy: Arc::new(Mutex::new(None)),
            state: Arc::new(Mutex::new(WebViewState::new())),
            is_running: Arc::new(Mutex::new(false)),
            background_color: bg,
        }
    }

    /// Set the root element and update the webview.
    ///
    /// Uses DOM patching to preserve CSS transitions and element state.
    #[pyo3(text_signature = "(self, element)")]
    fn set_root(&self, element: &Element) -> PyResult<()> {
        let is_running = self.event_proxy.lock().is_some();

        let mut state = self.state.lock();
        for (id, callback) in element.collect_callbacks() {
            state.callbacks.insert(id, callback);
        }

        if is_running {
            let json = render_to_json(&element.def);
            drop(state);
            if let Some(proxy) = self.event_proxy.lock().as_ref() {
                let _ = proxy.send_event(UserEvent::PatchRoot(json));
            }
        } else {
            state.pending_html = Some(render_to_html(&element.def));
        }

        Ok(())
    }

    /// Change the window title.
    ///
    /// Args:
    ///     title: The new title to display in the window header.
    #[pyo3(text_signature = "(self, title)")]
    fn set_title(&self, title: String) -> PyResult<()> {
        // Store in state for polling (used on Linux)
        self.state.lock().pending_title = Some(title.clone());

        // Also send via event proxy if available (used on other platforms)
        if let Some(proxy) = self.event_proxy.lock().as_ref() {
            let _ = proxy.send_event(UserEvent::SetTitle(title));
        }
        Ok(())
    }

    /// Update a single element by its ID without replacing the entire root.
    ///
    /// This is more efficient than set_root() when only a small part of the UI changes.
    /// The element must have an id set via the id() builder method.
    ///
    /// Args:
    ///     element_id: The ID of the element to update (set via id()).
    ///     element: The new Element to replace the existing one.
    #[pyo3(text_signature = "(self, element_id, element)")]
    fn update_element(&self, element_id: String, element: &Element) -> PyResult<()> {
        let json = {
            let mut state = self.state.lock();
            for (id, callback) in element.collect_callbacks() {
                state.callbacks.insert(id, callback);
            }

            let json = render_to_json_partial(&element.def);

            // Store as pending for Linux polling
            state.pending_element_updates.push((element_id.clone(), json.clone()));
            json
        };

        // Send update to webview if already running
        if let Some(proxy) = self.event_proxy.lock().as_ref() {
            let _ = proxy.send_event(UserEvent::PatchElement(element_id, json));
        }

        Ok(())
    }

    /// Show the window and start the event loop.
    ///
    /// This is blocking and will run until the window is closed. Call set_root() before
    /// or after this to update what's displayed.
    #[pyo3(text_signature = "(self)")]
    fn run(&self, py: Python) -> PyResult<()> {
        let title = self.title.clone();
        let width = self.width;
        let height = self.height;
        let state = self.state.clone();
        let event_proxy_holder = self.event_proxy.clone();
        let is_running = self.is_running.clone();
        let background_color = self.background_color;

        // Release GIL while running the event loop
        #[allow(deprecated)]
        py.allow_threads(|| {
            run_event_loop(title, width, height, state, event_proxy_holder, is_running, background_color)
        })
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))
    }

    /// Close the window and stop the event loop.
    #[pyo3(text_signature = "(self)")]
    fn close(&self) -> PyResult<()> {
        // Set close flag in state for polling (used on Linux)
        self.state.lock().should_close = true;

        // Also send via event proxy if available (used on other platforms)
        if let Some(proxy) = self.event_proxy.lock().as_ref() {
            let _ = proxy.send_event(UserEvent::Close);
        }
        Ok(())
    }

    /// Check if the window is currently running.
    ///
    /// Returns:
    ///     True if the event loop is active, False otherwise.
    #[pyo3(text_signature = "(self)")]
    fn is_running(&self) -> bool {
        *self.is_running.lock()
    }

    fn __repr__(&self) -> String {
        format!(
            "UiWindow(title='{}', size={}x{})",
            self.title, self.width, self.height
        )
    }
}

#[cfg(target_os = "linux")]
fn run_event_loop(
    title: String,
    width: u32,
    height: u32,
    state: Arc<Mutex<WebViewState>>,
    event_proxy_holder: Arc<Mutex<Option<EventLoopProxy<UserEvent>>>>,
    is_running: Arc<Mutex<bool>>,
    background_color: (u8, u8, u8, u8),
) -> Result<(), String> {
    use gtk::glib;
    use std::cell::RefCell;
    use std::rc::Rc;
    use std::sync::mpsc;

    gtk::init().map_err(|e| format!("Failed to initialize GTK: {:?}", e))?;

    // Create a channel for internal events
    let (event_tx, event_rx) = mpsc::channel::<UserEvent>();
    let event_rx = Rc::new(RefCell::new(event_rx));

    let state_clone = state.clone();

    // Create GTK window
    let window = gtk::Window::new(gtk::WindowType::Toplevel);
    window.set_title(&title);
    window.set_default_size(width as i32, height as i32);

    // Create a box to hold the webview
    let gtk_box = GtkBox::new(Orientation::Vertical, 0);
    gtk_box.set_vexpand(true);
    gtk_box.set_hexpand(true);

    // Get initial HTML
    let initial_content = {
        let state = state_clone.lock();
        state.pending_html.clone()
    };

    let initial_html = get_initial_html(initial_content.as_deref(), background_color);

    // Create IPC handler for callbacks
    let state_for_ipc = state_clone.clone();
    let ipc_handler = move |request: wry::http::Request<String>| {
        let body = request.body();
        if let Ok(event) = serde_json::from_str::<IpcEvent>(body) {
            // Handle click and mouse events (no arguments)
            if matches!(event.event_type.as_str(), "click" | "mouse_enter" | "mouse_leave" | "mouse_down" | "mouse_up") {
                if let Some(ref callback_id) = event.callback_id {
                    let state_for_cb = state_for_ipc.clone();
                    let callback_id = callback_id.clone();
                    #[allow(deprecated)]
                    Python::with_gil(|py| {
                        let callback = {
                            let state = state_for_cb.lock();
                            state.callbacks.get(&callback_id).map(|cb| cb.clone_ref(py))
                        };

                        if let Some(callback) = callback {
                            std::thread::spawn(move || {
                                #[allow(deprecated)]
                                Python::with_gil(|py| {
                                    if let Err(e) = callback.call0(py) {
                                        eprintln!("Callback error: {:?}", e);
                                    }
                                });
                            });
                        }
                    });
                }
            }

            if event.event_type == "input" || event.event_type == "change" {
                if let (Some(callback_id), Some(value)) = (&event.callback_id, event.value) {
                    let state_for_cb = state_for_ipc.clone();
                    let callback_id = callback_id.clone();
                    #[allow(deprecated)]
                    Python::with_gil(|py| {
                        let callback = {
                            let state = state_for_cb.lock();
                            state.callbacks.get(&callback_id).map(|cb| cb.clone_ref(py))
                        };

                        if let Some(callback) = callback {
                            std::thread::spawn(move || {
                                #[allow(deprecated)]
                                Python::with_gil(|py| {
                                    if let Err(e) = callback.call1(py, (value,)) {
                                        eprintln!("Input/change callback error: {:?}", e);
                                    }
                                });
                            });
                        }
                    });
                }
            }
        }
    };

    // Build webview with GTK
    let webview = WebViewBuilder::new()
        .with_html(initial_html)
        .with_ipc_handler(ipc_handler)
        .with_background_color(background_color)
        .build_gtk(&gtk_box)
        .map_err(|e| format!("Failed to build webview: {}", e))?;

    let webview = Rc::new(webview);

    window.add(&gtk_box);

    // Handle window close
    let is_running_for_close = is_running.clone();
    window.connect_delete_event(move |_, _| {
        *is_running_for_close.lock() = false;
        gtk::main_quit();
        glib::Propagation::Stop
    });

    window.show_all();

    *is_running.lock() = true;

    // Set up a polling loop to check for events from Python
    let webview_for_poll = webview.clone();
    let window_for_poll = window.clone();
    let is_running_for_poll = is_running.clone();
    glib::timeout_add_local(std::time::Duration::from_millis(16), move || {
        // Check for events
        while let Ok(event) = event_rx.borrow().try_recv() {
            match event {
                UserEvent::PatchRoot(json) => {
                    let js = format!("patchRoot({});", json);
                    let _ = webview_for_poll.evaluate_script(&js);
                }
                UserEvent::PatchElement(id, json) => {
                    let js = format!(
                        "patchElementById({}, {});",
                        serde_json::to_string(&id).unwrap(),
                        json
                    );
                    let _ = webview_for_poll.evaluate_script(&js);
                }
                UserEvent::SetTitle(title) => {
                    window_for_poll.set_title(&title);
                }
                UserEvent::Close => {
                    *is_running_for_poll.lock() = false;
                    gtk::main_quit();
                    return glib::ControlFlow::Break;
                }
            }
        }
        glib::ControlFlow::Continue
    });

    // Handle Ctrl+C (SIGINT) to close the window gracefully
    let is_running_for_sigint = is_running.clone();
    let window_for_sigint = window.clone();
    glib::unix_signal_add_local(libc::SIGINT, move || {
        *is_running_for_sigint.lock() = false;
        window_for_sigint.close();
        gtk::main_quit();
        glib::ControlFlow::Break
    });

    // Poll the state for pending changes from Python
    // This is needed because EventLoopProxy doesn't work with GTK
    let state_for_poll = state.clone();
    glib::timeout_add_local(std::time::Duration::from_millis(50), move || {
        let mut state = state_for_poll.lock();

        // Clear pending_html on first poll (already used for initial render)
        state.pending_html.take();

        // Check for pending element updates
        for (id, json) in state.pending_element_updates.drain(..) {
            let _ = event_tx.send(UserEvent::PatchElement(id, json));
        }

        // Check for pending title update
        if let Some(title) = state.pending_title.take() {
            let _ = event_tx.send(UserEvent::SetTitle(title));
        }

        // Check for close request
        if state.should_close {
            state.should_close = false;
            let _ = event_tx.send(UserEvent::Close);
        }

        glib::ControlFlow::Continue
    });

    gtk::main();
    *is_running.lock() = false;

    // Clear the event proxy
    *event_proxy_holder.lock() = None;

    Ok(())
}

#[cfg(not(target_os = "linux"))]
fn run_event_loop(
    title: String,
    width: u32,
    height: u32,
    state: Arc<Mutex<WebViewState>>,
    event_proxy_holder: Arc<Mutex<Option<EventLoopProxy<UserEvent>>>>,
    is_running: Arc<Mutex<bool>>,
    background_color: (u8, u8, u8, u8),
) -> Result<(), String> {
    // NVIDIA + Wayland workaround (not needed when using GTK backend)
    #[cfg(target_os = "linux")]
    {
        if std::path::Path::new("/dev/dri").exists()
            && std::env::var("WAYLAND_DISPLAY").is_ok()
            && std::env::var("XDG_SESSION_TYPE").unwrap_or_default() == "wayland"
        {
            unsafe {
                std::env::set_var("__NV_DISABLE_EXPLICIT_SYNC", "1");
            }
        }
    }

    let event_loop: EventLoop<UserEvent> = EventLoopBuilder::with_user_event().build();

    // Store the proxy so Python can send events
    *event_proxy_holder.lock() = Some(event_loop.create_proxy());
    *is_running.lock() = true;

    let window = WindowBuilder::new()
        .with_title(&title)
        .with_inner_size(tao::dpi::LogicalSize::new(width, height))
        .build(&event_loop)
        .map_err(|e| e.to_string())?;

    // Get pending HTML or use default
    let initial_content = {
        let state = state.lock();
        state.pending_html.clone()
    };

    let initial_html = get_initial_html(initial_content.as_deref(), background_color);

    // Create IPC handler for callbacks
    let state_clone = state.clone();
    let _proxy_for_callbacks = event_loop.create_proxy();

    let ipc_handler = move |request: wry::http::Request<String>| {
        let body = request.body();
        if let Ok(event) = serde_json::from_str::<IpcEvent>(body) {
            // Handle click and mouse events (no arguments)
            if matches!(event.event_type.as_str(), "click" | "mouse_enter" | "mouse_leave" | "mouse_down" | "mouse_up") {
                if let Some(ref callback_id) = event.callback_id {
                    let state_for_cb = state_clone.clone();
                    let callback_id = callback_id.clone();
                    #[allow(deprecated)]
                    Python::with_gil(|py| {
                        let callback = {
                            let state = state_for_cb.lock();
                            state.callbacks.get(&callback_id).map(|cb| cb.clone_ref(py))
                        };

                        if let Some(callback) = callback {
                            std::thread::spawn(move || {
                                #[allow(deprecated)]
                                Python::with_gil(|py| {
                                    if let Err(e) = callback.call0(py) {
                                        eprintln!("Callback error: {:?}", e);
                                    }
                                });
                            });
                        }
                    });
                }
            }

            if event.event_type == "input" || event.event_type == "change" {
                if let (Some(callback_id), Some(value)) = (&event.callback_id, event.value) {
                    let state_for_cb = state_clone.clone();
                    let callback_id = callback_id.clone();
                    #[allow(deprecated)]
                    Python::with_gil(|py| {
                        let callback = {
                            let state = state_for_cb.lock();
                            state.callbacks.get(&callback_id).map(|cb| cb.clone_ref(py))
                        };

                        if let Some(callback) = callback {
                            std::thread::spawn(move || {
                                #[allow(deprecated)]
                                Python::with_gil(|py| {
                                    if let Err(e) = callback.call1(py, (value,)) {
                                        eprintln!("Input/change callback error: {:?}", e);
                                    }
                                });
                            });
                        }
                    });
                }
            }
        }
    };

    let webview = WebViewBuilder::new()
        .with_html(initial_html)
        .with_ipc_handler(ipc_handler)
        .with_background_color(background_color)
        .build(&window)
        .map_err(|e| e.to_string())?;

    // Clear pending_html (already used for initial render)
    state.lock().pending_html.take();

    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Wait;

        match event {
            Event::WindowEvent {
                event: WindowEvent::CloseRequested,
                ..
            } => {
                *is_running.lock() = false;
                *control_flow = ControlFlow::Exit;
            }

            Event::UserEvent(user_event) => match user_event {
                UserEvent::PatchRoot(json) => {
                    let js = format!("patchRoot({});", json);
                    let _ = webview.evaluate_script(&js);
                }
                UserEvent::PatchElement(id, json) => {
                    let js = format!(
                        "patchElementById({}, {});",
                        serde_json::to_string(&id).unwrap(),
                        json
                    );
                    let _ = webview.evaluate_script(&js);
                }
                UserEvent::SetTitle(title) => {
                    window.set_title(&title);
                }
                UserEvent::Close => {
                    *is_running.lock() = false;
                    *control_flow = ControlFlow::Exit;
                }
            },

            _ => {}
        }
    });

    #[allow(unreachable_code)]
    {
        *event_proxy_holder.lock() = None;
        Ok(())
    }
}

#[derive(serde::Deserialize)]
struct IpcEvent {
    event_type: String,
    callback_id: Option<String>,
    value: Option<String>,
}

/// Parse a hex color string like "#1a1a1a" or "#1a1a1aff" to RGBA tuple
fn parse_hex_color(hex: &str) -> Option<(u8, u8, u8, u8)> {
    let hex = hex.trim_start_matches('#');
    match hex.len() {
        6 => {
            let r = u8::from_str_radix(&hex[0..2], 16).ok()?;
            let g = u8::from_str_radix(&hex[2..4], 16).ok()?;
            let b = u8::from_str_radix(&hex[4..6], 16).ok()?;
            Some((r, g, b, 255))
        }
        8 => {
            let r = u8::from_str_radix(&hex[0..2], 16).ok()?;
            let g = u8::from_str_radix(&hex[2..4], 16).ok()?;
            let b = u8::from_str_radix(&hex[4..6], 16).ok()?;
            let a = u8::from_str_radix(&hex[6..8], 16).ok()?;
            Some((r, g, b, a))
        }
        _ => None,
    }
}

fn get_initial_html(content: Option<&str>, background_color: (u8, u8, u8, u8)) -> String {
    let root_content = content.unwrap_or(r#"<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#666;">Loading...</div>"#);
    let (r, g, b, _a) = background_color;

    format!(
        r#"<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: rgb({}, {}, {});
            color: #ffffff;
            min-height: 100vh;
        }}
        #root {{
            width: 100%;
            height: 100vh;
        }}
        .size-full {{
            width: 100%;
            height: 100%;
        }}
        .flex-row {{ display: flex; flex-direction: row; }}
        .flex-col {{ display: flex; flex-direction: column; }}
        .items-center {{ align-items: center; }}
        .items-start {{ align-items: flex-start; }}
        .items-end {{ align-items: flex-end; }}
        .justify-center {{ justify-content: center; }}
        .justify-between {{ justify-content: space-between; }}
        .justify-start {{ justify-content: flex-start; }}
        .justify-end {{ justify-content: flex-end; }}
        button:focus, button:focus-visible,
        input:focus, input:focus-visible,
        select:focus, select:focus-visible {{
            outline: none;
        }}
    </style>
</head>
<body>
    <div id="root">{}</div>
    <script>
        function handleClick(callbackId) {{
            window.ipc.postMessage(JSON.stringify({{
                event_type: 'click',
                callback_id: callbackId
            }}));
        }}

        function handleInput(callbackId, value) {{
            window.ipc.postMessage(JSON.stringify({{
                event_type: 'input',
                callback_id: callbackId,
                value: value
            }}));
        }}

        function handleMouseEvent(callbackId, eventType) {{
            window.ipc.postMessage(JSON.stringify({{
                event_type: eventType,
                callback_id: callbackId
            }}));
        }}

        function patchElementById(elementId, t) {{
            var el = document.getElementById(elementId);
            if (el) {{
                var expectedTag = getTagForType(t.element_type);
                if (el.tagName === expectedTag) {{
                    patchElement(el, t);
                    patchChildren(el, t.children || []);
                }} else {{
                    var newEl = renderElement(t);
                    el.replaceWith(newEl);
                }}
            }} else {{
                console.warn('Element not found: ' + elementId);
            }}
        }}

        function handleChange(callbackId, value) {{
            window.ipc.postMessage(JSON.stringify({{
                event_type: 'change',
                callback_id: callbackId,
                value: String(value)
            }}));
        }}

        function buildStyleString(t) {{
            var s = [];
            
            // Element-type specific defaults
            if (t.element_type === 'button') {{
                s.push('cursor: ' + (t.cursor || 'pointer'));
                s.push('border: ' + (t.border_width != null ? t.border_width + 'px solid ' + (t.border_color || '#333') : 'none'));
                s.push('outline: none');
                s.push('font-size: ' + (t.font_size != null ? t.font_size + 'px' : '14px'));
                s.push('background: ' + (t.background_color || '#3b82f6'));
                s.push('color: ' + (t.text_color || 'white'));
                s.push('border-radius: ' + (t.border_radius != null ? t.border_radius + 'px' : '6px'));
                s.push('padding: ' + (t.padding != null ? t.padding + 'px' : '8px 16px'));
            }} else if (t.element_type === 'input') {{
                s.push('outline: none');
                s.push('padding: ' + (t.padding != null ? t.padding + 'px' : '8px 12px'));
                s.push('border: ' + (t.border_width != null ? t.border_width + 'px solid ' + (t.border_color || '#555') : '1px solid #555'));
                s.push('border-radius: ' + (t.border_radius != null ? t.border_radius + 'px' : '4px'));
                s.push('background: ' + (t.background_color || '#2a2a3a'));
                s.push('color: ' + (t.text_color || 'white'));
                s.push('font-size: ' + (t.font_size != null ? t.font_size + 'px' : '14px'));
                if (t.cursor) s.push('cursor: ' + t.cursor);
            }} else if (t.element_type === 'select') {{
                s.push('outline: none');
                s.push('padding: ' + (t.padding != null ? t.padding + 'px' : '8px 12px'));
                s.push('font-size: ' + (t.font_size != null ? t.font_size + 'px' : '14px'));
                s.push('cursor: ' + (t.cursor || 'pointer'));
                if (t.background_color) s.push('background: ' + t.background_color);
                if (t.text_color) s.push('color: ' + t.text_color);
                if (t.border_radius != null) s.push('border-radius: ' + t.border_radius + 'px');
                if (t.border_width != null) s.push('border: ' + t.border_width + 'px solid ' + (t.border_color || '#333'));
            }} else {{
                // Generic elements (div, span, etc.)
                if (t.size_full) {{ s.push('width: 100%'); s.push('height: 100%'); }}
                if (t.background_color) s.push('background-color: ' + t.background_color);
                if (t.text_color) s.push('color: ' + t.text_color);
                if (t.border_radius != null) s.push('border-radius: ' + t.border_radius + 'px');
                if (t.border_width != null && t.border_color) s.push('border: ' + t.border_width + 'px solid ' + t.border_color);
                if (t.padding != null) s.push('padding: ' + t.padding + 'px');
                if (t.font_size != null) s.push('font-size: ' + t.font_size + 'px');
                if (t.cursor) s.push('cursor: ' + t.cursor);
            }}
            
            // Common properties for all element types
            if (t.width != null) s.push('width: ' + t.width + 'px');
            if (t.height != null) s.push('height: ' + t.height + 'px');
            if (t.min_width != null) s.push('min-width: ' + t.min_width + 'px');
            if (t.max_width != null) s.push('max-width: ' + t.max_width + 'px');
            if (t.min_height != null) s.push('min-height: ' + t.min_height + 'px');
            if (t.max_height != null) s.push('max-height: ' + t.max_height + 'px');
            if (t.flex_direction) s.push('display: flex; flex-direction: ' + t.flex_direction);
            if (t.align_items) s.push('align-items: ' + t.align_items);
            if (t.justify_content) s.push('justify-content: ' + t.justify_content);
            if (t.gap != null) s.push('gap: ' + t.gap + 'px');
            if (t.flex_wrap) s.push('flex-wrap: ' + t.flex_wrap);
            if (t.flex_grow != null) s.push('flex-grow: ' + t.flex_grow);
            if (t.flex_shrink != null) s.push('flex-shrink: ' + t.flex_shrink);
            if (t.flex_basis) s.push('flex-basis: ' + t.flex_basis);
            if (t.align_self) s.push('align-self: ' + t.align_self);
            if (t.display_grid) s.push('display: grid');
            if (t.grid_template_columns) s.push('grid-template-columns: ' + t.grid_template_columns);
            if (t.grid_template_rows) s.push('grid-template-rows: ' + t.grid_template_rows);
            if (t.grid_column) s.push('grid-column: ' + t.grid_column);
            if (t.grid_row) s.push('grid-row: ' + t.grid_row);
            if (t.place_items) s.push('place-items: ' + t.place_items);
            if (t.padding_top != null) s.push('padding-top: ' + t.padding_top + 'px');
            if (t.padding_right != null) s.push('padding-right: ' + t.padding_right + 'px');
            if (t.padding_bottom != null) s.push('padding-bottom: ' + t.padding_bottom + 'px');
            if (t.padding_left != null) s.push('padding-left: ' + t.padding_left + 'px');
            if (t.margin != null) s.push('margin: ' + t.margin + 'px');
            if (t.margin_top != null) s.push('margin-top: ' + t.margin_top + 'px');
            if (t.margin_right != null) s.push('margin-right: ' + t.margin_right + 'px');
            if (t.margin_bottom != null) s.push('margin-bottom: ' + t.margin_bottom + 'px');
            if (t.margin_left != null) s.push('margin-left: ' + t.margin_left + 'px');
            if (t.border_radius_top_left != null) s.push('border-top-left-radius: ' + t.border_radius_top_left + 'px');
            if (t.border_radius_top_right != null) s.push('border-top-right-radius: ' + t.border_radius_top_right + 'px');
            if (t.border_radius_bottom_right != null) s.push('border-bottom-right-radius: ' + t.border_radius_bottom_right + 'px');
            if (t.border_radius_bottom_left != null) s.push('border-bottom-left-radius: ' + t.border_radius_bottom_left + 'px');
            if (t.border_width_top != null) s.push('border-top: ' + t.border_width_top + 'px solid ' + (t.border_color_top || t.border_color || '#333'));
            if (t.border_width_right != null) s.push('border-right: ' + t.border_width_right + 'px solid ' + (t.border_color_right || t.border_color || '#333'));
            if (t.border_width_bottom != null) s.push('border-bottom: ' + t.border_width_bottom + 'px solid ' + (t.border_color_bottom || t.border_color || '#333'));
            if (t.border_width_left != null) s.push('border-left: ' + t.border_width_left + 'px solid ' + (t.border_color_left || t.border_color || '#333'));
            if (t.overflow) s.push('overflow: ' + t.overflow);
            if (t.text_align) s.push('text-align: ' + t.text_align);
            if (t.word_wrap) s.push('word-wrap: ' + t.word_wrap);
            if (t.position) s.push('position: ' + t.position);
            if (t.top != null) s.push('top: ' + t.top + 'px');
            if (t.right != null) s.push('right: ' + t.right + 'px');
            if (t.bottom != null) s.push('bottom: ' + t.bottom + 'px');
            if (t.left != null) s.push('left: ' + t.left + 'px');
            if (t.font_weight) s.push('font-weight: ' + t.font_weight);
            if (t.transition) s.push('transition: ' + t.transition);
            if (t.opacity != null) s.push('opacity: ' + t.opacity);
            if (t.object_fit) s.push('object-fit: ' + t.object_fit);
            if (t.style) s.push(t.style);
            return s.join('; ');
        }}

        function buildStateStyles(t) {{
            var id = t.user_id || t.id;
            var css = '';
            var hover = [];
            var focus = [];
            
            // Add hover styles
            if (t.hover_bg) hover.push('background-color: ' + t.hover_bg + ' !important');
            if (t.hover_text_color) hover.push('color: ' + t.hover_text_color + ' !important');
            if (t.hover_border_color) hover.push('border-color: ' + t.hover_border_color + ' !important');
            if (t.hover_opacity != null) hover.push('opacity: ' + t.hover_opacity + ' !important');
            if (t.hover_scale != null) hover.push('transform: scale(' + t.hover_scale + ') !important');
            
            // For buttons, ensure cursor stays pointer on hover (unless disabled)
            if (t.element_type === 'button' && !t.disabled) {{
                hover.push('cursor: pointer !important');
            }}
            
            // Add focus styles
            if (t.focus_bg) focus.push('background-color: ' + t.focus_bg + ' !important');
            if (t.focus_text_color) focus.push('color: ' + t.focus_text_color + ' !important');
            if (t.focus_border_color) focus.push('border-color: ' + t.focus_border_color + ' !important');
            
            // For buttons/inputs, ensure outline stays none on focus
            if (t.element_type === 'button' || t.element_type === 'input' || t.element_type === 'select') {{
                focus.push('outline: none !important');
            }}
            
            if (hover.length) css += '#' + id + ':hover {{ ' + hover.join('; ') + ' }} ';
            if (focus.length) css += '#' + id + ':focus {{ ' + focus.join('; ') + ' }} ';
            return css;
        }}

        function getTagForType(type) {{
            if (type === 'text') return 'SPAN';
            if (type === 'button') return 'BUTTON';
            if (type === 'image') return 'IMG';
            if (type === 'input') return 'INPUT';
            if (type === 'checkbox' || type === 'radio') return 'LABEL';
            if (type === 'select') return 'SELECT';
            return 'DIV';
        }}

        function patchAttrs(el, t) {{
            if (t.user_id && el.id !== t.user_id) el.id = t.user_id;
            if (t.class_names && t.class_names.length) {{
                el.className = t.class_names.join(' ');
            }} else if (el.className) {{
                el.className = '';
            }}
        }}

        function patchEvents(el, t) {{
            if (t.on_click) {{
                el.onclick = function() {{ handleClick(t.on_click); }};
            }} else {{
                el.onclick = null;
            }}
            if (t.on_mouse_enter) {{
                el.onmouseenter = function() {{ handleMouseEvent(t.on_mouse_enter, 'mouse_enter'); }};
            }} else {{
                el.onmouseenter = null;
            }}
            if (t.on_mouse_leave) {{
                el.onmouseleave = function() {{ handleMouseEvent(t.on_mouse_leave, 'mouse_leave'); }};
            }} else {{
                el.onmouseleave = null;
            }}
            if (t.on_mouse_down) {{
                el.onmousedown = function() {{ handleMouseEvent(t.on_mouse_down, 'mouse_down'); }};
            }} else {{
                el.onmousedown = null;
            }}
            if (t.on_mouse_up) {{
                el.onmouseup = function() {{ handleMouseEvent(t.on_mouse_up, 'mouse_up'); }};
            }} else {{
                el.onmouseup = null;
            }}
            if (t.on_input) {{
                el.oninput = function() {{ handleInput(t.on_input, el.value); }};
            }} else {{
                el.oninput = null;
            }}
            if (t.on_change) {{
                el.onchange = function() {{
                    var val = el.type === 'checkbox' ? el.checked : el.value;
                    handleChange(t.on_change, val);
                }};
            }} else {{
                el.onchange = null;
            }}
        }}

        function patchElement(el, t) {{
            var hadFocus = document.activeElement === el;
            patchAttrs(el, t);
            var newStyle = buildStyleString(t);
            if (el.style.cssText !== newStyle) {{
                el.style.cssText = newStyle;
            }}
            patchEvents(el, t);
            if (t.element_type === 'text' || t.element_type === 'button') {{
                var txt = t.text_content || '';
                if (el.textContent !== txt) el.textContent = txt;
            }}
            if (t.element_type === 'button') {{
                if (t.disabled) {{
                    el.disabled = true;
                }} else {{
                    el.disabled = false;
                }}
            }}
            if (t.element_type === 'input') {{
                if (t.placeholder && el.placeholder !== t.placeholder) el.placeholder = t.placeholder;
                if (t.value !== undefined && el.value !== t.value && document.activeElement !== el) el.value = t.value || '';
                if (t.disabled !== undefined) el.disabled = !!t.disabled;
            }}
            if (t.element_type === 'image') {{
                var src = t.text_content || '';
                if (el.src !== src) el.src = src;
                if (t.alt && el.alt !== t.alt) el.alt = t.alt;
            }}
            if (hadFocus && document.activeElement !== el) el.focus();
        }}

        function patchChildren(parent, newChildren) {{
            for (var i = 0; i < newChildren.length; i++) {{
                var nc = newChildren[i];
                var oldChild = parent.children[i];
                var expectedTag = getTagForType(nc.element_type);
                if (oldChild && oldChild.tagName === expectedTag) {{
                    patchElement(oldChild, nc);
                    patchChildren(oldChild, nc.children || []);
                }} else if (oldChild) {{
                    var newEl = renderElement(nc);
                    if (oldChild.dataset.wryId) newEl.setAttribute('data-wry-id', oldChild.dataset.wryId);
                    parent.replaceChild(newEl, oldChild);
                }} else {{
                    parent.appendChild(renderElement(nc));
                }}
            }}
            while (parent.children.length > newChildren.length) {{
                parent.removeChild(parent.lastChild);
            }}
        }}

        function renderElement(t) {{
            var tag = getTagForType(t.element_type);
            var el = document.createElement(tag);
            el.id = t.user_id || t.id;
            el.setAttribute('data-wry-id', t.id);
            el.style.cssText = buildStyleString(t);
            if (t.class_names && t.class_names.length) el.className = t.class_names.join(' ');
            patchEvents(el, t);
            if (t.element_type === 'text' || t.element_type === 'button') {{
                el.textContent = t.text_content || '';
            }}
            if (t.element_type === 'button' && t.disabled) {{
                el.disabled = true;
            }}
            if (t.element_type === 'input') {{
                el.type = 'text';
                if (t.placeholder) el.placeholder = t.placeholder;
                if (t.value) el.value = t.value;
                if (t.disabled) el.disabled = true;
            }}
            if (t.element_type === 'image') {{
                el.src = t.text_content || '';
                if (t.alt) el.alt = t.alt;
            }}
            var children = t.children || [];
            for (var i = 0; i < children.length; i++) {{
                el.appendChild(renderElement(children[i]));
            }}
            return el;
        }}

        function updateStateStyles(t) {{
            var styleId = 'wry-state-styles';
            var styleEl = document.getElementById(styleId);
            if (!styleEl) {{
                styleEl = document.createElement('style');
                styleEl.id = styleId;
                document.head.appendChild(styleEl);
            }}
            var css = '';
            function collectStyles(node) {{
                css += buildStateStyles(node);
                var children = node.children || [];
                for (var i = 0; i < children.length; i++) {{
                    collectStyles(children[i]);
                }}
            }}
            collectStyles(t);
            if (styleEl.textContent !== css) styleEl.textContent = css;
        }}

        function patchRoot(t) {{
            var rootEl = document.getElementById('root');
            var existing = rootEl.querySelector('[data-wry-id="' + t.id + '"]') || rootEl.children[0];
            if (!existing || existing.tagName !== getTagForType(t.element_type)) {{
                rootEl.innerHTML = '';
                rootEl.appendChild(renderElement(t));
            }} else {{
                patchElement(existing, t);
                patchChildren(existing, t.children || []);
            }}
            updateStateStyles(t);
        }}

    </script>
</body>
</html>"#,
        r, g, b, root_content
    )
}
