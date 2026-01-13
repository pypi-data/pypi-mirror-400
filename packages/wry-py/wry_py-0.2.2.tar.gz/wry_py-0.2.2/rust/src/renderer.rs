use crate::elements::ElementDef;
use percent_encoding::utf8_percent_encode;
use percent_encoding::NON_ALPHANUMERIC;
use std::path::Path;
use crate::assets;

/// Assign stable path-based IDs to elements for consistent DOM matching
fn assign_stable_ids(element: &mut ElementDef, path: &str) {
    element.id = path.to_string();
    for (i, child) in element.children.iter_mut().enumerate() {
        assign_stable_ids(child, &format!("{}-{}", path, i));
    }
}

/// Render an ElementDef tree to HTML string
pub fn render_to_html(element: &ElementDef) -> String {
    let mut elem = element.clone();
    assign_stable_ids(&mut elem, "r");
    render_element(&elem)
}

/// Serialize an ElementDef tree to JSON for DOM patching
pub fn render_to_json(element: &ElementDef) -> String {
    let mut elem = element.clone();
    assign_stable_ids(&mut elem, "r");
    serde_json::to_string(&elem).unwrap_or_default()
}

/// Serialize an ElementDef to JSON without reassigning IDs (for partial updates)
pub fn render_to_json_partial(element: &ElementDef) -> String {
    serde_json::to_string(element).unwrap_or_default()
}

/// Build hover/focus CSS styles for an element
fn build_state_styles(el: &ElementDef) -> String {
    let mut css = String::new();
    let id = escape_html(el.user_id.as_deref().unwrap_or(&el.id));

    // Hover styles
    let mut hover_styles = Vec::new();
    if let Some(ref bg) = el.hover_bg {
        hover_styles.push(format!("background-color: {} !important", bg));
    }
    if let Some(ref color) = el.hover_text_color {
        hover_styles.push(format!("color: {} !important", color));
    }
    if let Some(ref bc) = el.hover_border_color {
        hover_styles.push(format!("border-color: {} !important", bc));
    }
    if let Some(opacity) = el.hover_opacity {
        hover_styles.push(format!("opacity: {} !important", opacity));
    }
    if let Some(scale) = el.hover_scale {
        hover_styles.push(format!("transform: scale({}) !important", scale));
    }
    if !hover_styles.is_empty() {
        css.push_str(&format!("#{}:hover {{ {} }}", id, hover_styles.join("; ")));
    }

    // Focus styles
    let mut focus_styles = Vec::new();
    if let Some(ref bg) = el.focus_bg {
        focus_styles.push(format!("background-color: {} !important", bg));
    }
    if let Some(ref color) = el.focus_text_color {
        focus_styles.push(format!("color: {} !important", color));
    }
    if let Some(ref bc) = el.focus_border_color {
        focus_styles.push(format!("border-color: {} !important", bc));
    }
    if !focus_styles.is_empty() {
        css.push_str(&format!("#{}:focus {{ {} }}", id, focus_styles.join("; ")));
    }

    if css.is_empty() {
        String::new()
    } else {
        format!("<style>{}</style>", css)
    }
}

fn percent_encode_path(p: &Path) -> String {
    let s = p.to_string_lossy().replace('\\', "/");
    let encoded_segments: Vec<String> = s
        .split('/')
        .map(|seg| utf8_percent_encode(seg, NON_ALPHANUMERIC).to_string())
        .collect();
    let joined = encoded_segments.join("/");
    format!("file:///{}", joined.trim_start_matches('/'))
}

fn resolve_local_asset(path_str: &str) -> String {
    // Already a fully-qualified URL
    if path_str.starts_with("http://")
        || path_str.starts_with("https://")
        || path_str.starts_with("data:")
        || path_str.starts_with("file://")
    {
        return path_str.to_string();
    }

    // asset: prefix for explicit AssetCatalog lookup
    if let Some(name) = path_str.strip_prefix("asset:") {
        if let Some(uri) = assets::get_asset_data_uri(name) {
            return uri;
        }
    }

    // Check AssetCatalog by name or basename
    if let Some(uri) = assets::get_asset_data_uri(path_str) {
        return uri;
    }
    if let Some(basename) = Path::new(path_str).file_name().and_then(|s| s.to_str()) {
        if let Some(uri) = assets::get_asset_data_uri(basename) {
            return uri;
        }
    }

    // Fall back to file:// URL
    match std::fs::canonicalize(path_str) {
        Ok(p) => percent_encode_path(&p),
        Err(_) => path_str.to_string(),
    }
}

// Rewrite url(...) references inside CSS to resolve local paths
fn rewrite_css_urls(css: &str) -> String {
    let mut out = String::with_capacity(css.len());
    let mut idx = 0usize;
    while let Some(pos) = css[idx..].find("url(") {
        let start = idx + pos;
        out.push_str(&css[idx..start]);
        if let Some(end_rel) = css[start..].find(')') {
            let end = start + end_rel;
            let inner = &css[start + 4..end];
            let inner_trim = inner.trim().trim_matches(|c| c == '\'' || c == '"');
            let resolved = resolve_local_asset(inner_trim);
            out.push_str("url(\"");
            out.push_str(&resolved);
            out.push_str("\")");
            idx = end + 1;
        } else {
            out.push_str(&css[start..]);
            idx = css.len();
            break;
        }
    }
    if idx < css.len() {
        out.push_str(&css[idx..]);
    }
    out
}

// Build border-radius considering per-corner values
fn build_border_radius_style(el: &ElementDef) -> Option<String> {
    let tl = el.border_radius_top_left.or(el.border_radius);
    let tr = el.border_radius_top_right.or(el.border_radius);
    let br = el.border_radius_bottom_right.or(el.border_radius);
    let bl = el.border_radius_bottom_left.or(el.border_radius);

    if tl.is_none() && tr.is_none() && br.is_none() && bl.is_none() {
        None
    } else {
        let tl_v = tl.unwrap_or(0.0);
        let tr_v = tr.unwrap_or(tl_v);
        let br_v = br.unwrap_or(tl_v);
        let bl_v = bl.unwrap_or(tr_v);
        Some(format!("border-radius: {}px {}px {}px {}px", tl_v, tr_v, br_v, bl_v))
    }
}

// Build per-side border styles
fn build_border_sides_styles(el: &ElementDef) -> Vec<String> {
    let mut out = Vec::new();

    if let Some(w) = el.border_width_top {
        let color = el.border_color_top.as_deref().or(el.border_color.as_deref()).unwrap_or("#333");
        out.push(format!("border-top: {}px solid {}", w, color));
    }
    if let Some(w) = el.border_width_right {
        let color = el.border_color_right.as_deref().or(el.border_color.as_deref()).unwrap_or("#333");
        out.push(format!("border-right: {}px solid {}", w, color));
    }
    if let Some(w) = el.border_width_bottom {
        let color = el.border_color_bottom.as_deref().or(el.border_color.as_deref()).unwrap_or("#333");
        out.push(format!("border-bottom: {}px solid {}", w, color));
    }
    if let Some(w) = el.border_width_left {
        let color = el.border_color_left.as_deref().or(el.border_color.as_deref()).unwrap_or("#333");
        out.push(format!("border-left: {}px solid {}", w, color));
    }

    out
}

/// Build event handler attributes for an element
fn build_event_attrs(el: &ElementDef) -> String {
    let mut attrs = String::new();

    if let Some(ref cb_id) = el.on_click {
        attrs.push_str(&format!(" onclick=\"handleClick('{}')\"", escape_html(cb_id)));
    }
    if let Some(ref cb_id) = el.on_mouse_enter {
        attrs.push_str(&format!(" onmouseenter=\"handleMouseEvent('{}', 'mouse_enter')\"", escape_html(cb_id)));
    }
    if let Some(ref cb_id) = el.on_mouse_leave {
        attrs.push_str(&format!(" onmouseleave=\"handleMouseEvent('{}', 'mouse_leave')\"", escape_html(cb_id)));
    }
    if let Some(ref cb_id) = el.on_mouse_down {
        attrs.push_str(&format!(" onmousedown=\"handleMouseEvent('{}', 'mouse_down')\"", escape_html(cb_id)));
    }
    if let Some(ref cb_id) = el.on_mouse_up {
        attrs.push_str(&format!(" onmouseup=\"handleMouseEvent('{}', 'mouse_up')\"", escape_html(cb_id)));
    }

    attrs
}

fn render_element(el: &ElementDef) -> String {
    match el.element_type.as_str() {
        "text" => render_text(el),
        "button" => render_button(el),
        "image" => render_image(el),
        "input" => render_input(el),
        "checkbox" => render_checkbox(el),
        "radio" => render_radio(el),
        "select" => render_select(el),
        _ => render_div(el),
    }
}

/// Get the element ID to use in HTML (user_id if set, otherwise internal id)
fn get_element_id(el: &ElementDef) -> &str {
    el.user_id.as_deref().unwrap_or(&el.id)
}

/// Build data-id attribute for internal element tracking
fn build_data_id_attr(el: &ElementDef) -> String {
    format!(" data-wry-id=\"{}\"", escape_html(&el.id))
}

fn render_div(el: &ElementDef) -> String {
    let mut classes = Vec::new();
    let mut styles = Vec::new();

    for class in &el.class_names {
        classes.push(class.as_str());
    }

    if el.size_full {
        classes.push("size-full");
    }

    match el.flex_direction.as_deref() {
        Some("column") => classes.push("flex-col"),
        Some("row") => classes.push("flex-row"),
        _ => {}
    }

    match el.align_items.as_deref() {
        Some("center") => classes.push("items-center"),
        Some("start") | Some("flex-start") => classes.push("items-start"),
        Some("end") | Some("flex-end") => classes.push("items-end"),
        _ => {}
    }

    match el.justify_content.as_deref() {
        Some("center") => classes.push("justify-center"),
        Some("space-between") => classes.push("justify-between"),
        Some("start") | Some("flex-start") => classes.push("justify-start"),
        Some("end") | Some("flex-end") => classes.push("justify-end"),
        _ => {}
    }

    if el.display_grid {
        styles.push("display: grid".to_string());
    }
    if let Some(ref cols) = el.grid_template_columns {
        styles.push(format!("grid-template-columns: {}", cols));
    }
    if let Some(ref rows) = el.grid_template_rows {
        styles.push(format!("grid-template-rows: {}", rows));
    }
    if let Some(ref col) = el.grid_column {
        styles.push(format!("grid-column: {}", col));
    }
    if let Some(ref row) = el.grid_row {
        styles.push(format!("grid-row: {}", row));
    }
    if let Some(ref pi) = el.place_items {
        styles.push(format!("place-items: {}", pi));
    }

    if let Some(w) = el.width {
        styles.push(format!("width: {}px", w));
    }
    if let Some(h) = el.height {
        styles.push(format!("height: {}px", h));
    }
    if let Some(mw) = el.min_width {
        styles.push(format!("min-width: {}px", mw));
    }
    if let Some(mw) = el.max_width {
        styles.push(format!("max-width: {}px", mw));
    }
    if let Some(mh) = el.min_height {
        styles.push(format!("min-height: {}px", mh));
    }
    if let Some(mh) = el.max_height {
        styles.push(format!("max-height: {}px", mh));
    }
    if let Some(g) = el.gap {
        styles.push(format!("gap: {}px", g));
    }
    if let Some(ref fw) = el.flex_wrap {
        styles.push(format!("flex-wrap: {}", fw));
    }
    if let Some(fg) = el.flex_grow {
        styles.push(format!("flex-grow: {}", fg));
    }
    if let Some(fs) = el.flex_shrink {
        styles.push(format!("flex-shrink: {}", fs));
    }
    if let Some(ref fb) = el.flex_basis {
        styles.push(format!("flex-basis: {}", fb));
    }
    if let Some(ref align_self) = el.align_self {
        styles.push(format!("align-self: {}", align_self));
    }
    if let Some(p) = el.padding {
        styles.push(format!("padding: {}px", p));
    }

    if let Some(pt) = el.padding_top {
        styles.push(format!("padding-top: {}px", pt));
    }
    if let Some(pr) = el.padding_right {
        styles.push(format!("padding-right: {}px", pr));
    }
    if let Some(pb) = el.padding_bottom {
        styles.push(format!("padding-bottom: {}px", pb));
    }
    if let Some(pl) = el.padding_left {
        styles.push(format!("padding-left: {}px", pl));
    }
    if let Some(m) = el.margin {
        styles.push(format!("margin: {}px", m));
    }
    if let Some(ref bg) = el.background_color {
        styles.push(format!("background-color: {}", bg));
    }
    if let Some(ref tc) = el.text_color {
        styles.push(format!("color: {}", tc));
    }

    if let Some(mt) = el.margin_top {
        styles.push(format!("margin-top: {}px", mt));
    }
    if let Some(mr) = el.margin_right {
        styles.push(format!("margin-right: {}px", mr));
    }
    if let Some(mb) = el.margin_bottom {
        styles.push(format!("margin-bottom: {}px", mb));
    }
    if let Some(ml) = el.margin_left {
        styles.push(format!("margin-left: {}px", ml));
    }

    if let Some(br_style) = build_border_radius_style(el) {
        styles.push(br_style);
    } else if let Some(br) = el.border_radius {
        styles.push(format!("border-radius: {}px", br));
    }

    let side_border_styles = build_border_sides_styles(el);
    if !side_border_styles.is_empty() {
        styles.extend(side_border_styles);
    } else if let Some(bw) = el.border_width {
        let bc = el.border_color.as_deref().unwrap_or("#333");
        styles.push(format!("border: {}px solid {}", bw, bc));
    }

    if let Some(ref overflow) = el.overflow {
        styles.push(format!("overflow: {}", overflow));
    }
    if let Some(ref text_align) = el.text_align {
        styles.push(format!("text-align: {}", text_align));
    }
    if let Some(ref word_wrap) = el.word_wrap {
        styles.push(format!("word-wrap: {}", word_wrap));
    }
    if let Some(ref position) = el.position {
        styles.push(format!("position: {}", position));
    }
    if let Some(top) = el.top {
        styles.push(format!("top: {}px", top));
    }
    if let Some(right) = el.right {
        styles.push(format!("right: {}px", right));
    }
    if let Some(bottom) = el.bottom {
        styles.push(format!("bottom: {}px", bottom));
    }
    if let Some(left) = el.left {
        styles.push(format!("left: {}px", left));
    }
    if let Some(fs) = el.font_size {
        styles.push(format!("font-size: {}px", fs));
    }
    if let Some(ref fw) = el.font_weight {
        styles.push(format!("font-weight: {}", fw));
    }
    if let Some(ref transition) = el.transition {
        styles.push(format!("transition: {}", transition));
    }
    if let Some(opacity) = el.opacity {
        styles.push(format!("opacity: {}", opacity));
    }
    if let Some(ref cursor) = el.cursor {
        styles.push(format!("cursor: {}", cursor));
    }

    if let Some(ref raw) = el.style {
        let rewritten = rewrite_css_urls(raw);
        styles.push(escape_html(&rewritten));
    }

    let class_attr = if classes.is_empty() {
        String::new()
    } else {
        format!(" class=\"{}\"", classes.join(" "))
    };

    let style_attr = if styles.is_empty() {
        String::new()
    } else {
        format!(" style=\"{}\"", styles.join("; "))
    };

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let data_id_attr = build_data_id_attr(el);

    let children_html: String = el.children.iter().map(render_element).collect();
    let text_content = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    format!(
        "{}<div id=\"{}\"{}{}{}{}>{}{}</div>",
        state_styles,
        escape_html(get_element_id(el)),
        data_id_attr,
        class_attr,
        style_attr,
        event_attrs,
        text_content,
        children_html
    )
}

fn render_text(el: &ElementDef) -> String {
    let mut styles = Vec::new();

    if let Some(ref tc) = el.text_color {
        styles.push(format!("color: {}", tc));
    }
    if let Some(fs) = el.font_size {
        styles.push(format!("font-size: {}px", fs));
    }
    if let Some(ref fw) = el.font_weight {
        styles.push(format!("font-weight: {}", fw));
    }
    if let Some(ref text_align) = el.text_align {
        styles.push(format!("text-align: {}", text_align));
    }
    if let Some(ref word_wrap) = el.word_wrap {
        styles.push(format!("word-wrap: {}", word_wrap));
    }
    if let Some(p) = el.padding {
        styles.push(format!("padding: {}px", p));
    }
    if let Some(ref transition) = el.transition {
        styles.push(format!("transition: {}", transition));
    }

    let style_attr = if styles.is_empty() {
        String::new()
    } else {
        format!(" style=\"{}\"", styles.join("; "))
    };

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let data_id_attr = build_data_id_attr(el);
    let text = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    let class_attr = if el.class_names.is_empty() {
        String::new()
    } else {
        format!(" class=\"{}\"", el.class_names.join(" "))
    };

    format!(
        "{}<span id=\"{}\"{}{}{}{}>{}</span>",
        state_styles,
        escape_html(get_element_id(el)),
        data_id_attr,
        class_attr,
        style_attr,
        event_attrs,
        text
    )
}

fn render_button(el: &ElementDef) -> String {
    let mut styles = vec![
        "cursor: pointer".to_string(),
        "padding: 8px 16px".to_string(),
        "border: none".to_string(),
        "border-radius: 6px".to_string(),
        "background: #3b82f6".to_string(),
        "color: white".to_string(),
        "font-size: 14px".to_string(),
        "outline: none".to_string(),
    ];

    if let Some(ref bg) = el.background_color {
        styles.retain(|s| !s.starts_with("background:"));
        styles.push(format!("background: {}", bg));
    }
    if let Some(ref tc) = el.text_color {
        styles.retain(|s| !s.starts_with("color:"));
        styles.push(format!("color: {}", tc));
    }
    if let Some(br_style) = build_border_radius_style(el) {
        styles.retain(|s| !s.starts_with("border-radius:"));
        styles.push(br_style);
    } else if let Some(br) = el.border_radius {
        styles.retain(|s| !s.starts_with("border-radius:"));
        styles.push(format!("border-radius: {}px", br));
    }
    if let Some(fs) = el.font_size {
        styles.retain(|s| !s.starts_with("font-size:"));
        styles.push(format!("font-size: {}px", fs));
    }
    if let Some(p) = el.padding {
        styles.retain(|s| !s.starts_with("padding:"));
        styles.push(format!("padding: {}px", p));
    }

    let side_border_styles = build_border_sides_styles(el);
    if !side_border_styles.is_empty() {
        styles.retain(|s| !s.starts_with("border:"));
        styles.extend(side_border_styles);
    } else if let Some(bw) = el.border_width {
        styles.retain(|s| !s.starts_with("border:"));
        let bc = el.border_color.as_deref().unwrap_or("#333");
        styles.push(format!("border: {}px solid {}", bw, bc));
    }

    if let Some(ref cursor) = el.cursor {
        styles.retain(|s| !s.starts_with("cursor:"));
        styles.push(format!("cursor: {}", cursor));
    }
    if let Some(ref transition) = el.transition {
        styles.push(format!("transition: {}", transition));
    }
    if let Some(opacity) = el.opacity {
        styles.push(format!("opacity: {}", opacity));
    }

    if let Some(ref raw) = el.style {
        let rewritten = rewrite_css_urls(raw);
        styles.push(escape_html(&rewritten));
    }

    let style_attr = format!(" style=\"{}\"", styles.join("; "));
    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let data_id_attr = build_data_id_attr(el);
    let text = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    let class_attr = if el.class_names.is_empty() {
        String::new()
    } else {
        format!(" class=\"{}\"", el.class_names.join(" "))
    };

    format!(
        "{}<button id=\"{}\"{}{}{}{}>{}</button>",
        state_styles,
        escape_html(get_element_id(el)),
        data_id_attr,
        class_attr,
        style_attr,
        event_attrs,
        text
    )
}

fn render_image(el: &ElementDef) -> String {
    let mut styles = Vec::new();

    if let Some(w) = el.width {
        styles.push(format!("width: {}px", w));
    }
    if let Some(h) = el.height {
        styles.push(format!("height: {}px", h));
    }
    if let Some(br_style) = build_border_radius_style(el) {
        styles.push(br_style);
    } else if let Some(br) = el.border_radius {
        styles.push(format!("border-radius: {}px", br));
    }
    if let Some(ref of) = el.object_fit {
        styles.push(format!("object-fit: {}", of));
    }
    if let Some(ref transition) = el.transition {
        styles.push(format!("transition: {}", transition));
    }
    if let Some(opacity) = el.opacity {
        styles.push(format!("opacity: {}", opacity));
    }
    if let Some(ref cursor) = el.cursor {
        styles.push(format!("cursor: {}", cursor));
    }

    let side_border_styles = build_border_sides_styles(el);
    if !side_border_styles.is_empty() {
        styles.retain(|s| !s.starts_with("border:"));
        styles.extend(side_border_styles);
    }

    let style_attr = if styles.is_empty() {
        String::new()
    } else {
        format!(" style=\"{}\"", styles.join("; "))
    };

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let data_id_attr = build_data_id_attr(el);

    let raw_src = el.text_content.as_ref().map(|t| t.as_str()).unwrap_or("");
    let resolved_src = resolve_local_asset(raw_src);
    let src = escape_html(&resolved_src);
    let alt_attr = el.alt.as_ref()
        .map(|a| format!(" alt=\"{}\"", escape_html(a)))
        .unwrap_or_default();

    let class_attr = if el.class_names.is_empty() {
        String::new()
    } else {
        format!(" class=\"{}\"", el.class_names.join(" "))
    };

    format!(
        "{}<img id=\"{}\"{}{}src=\"{}\"{}{}{}/>",
        state_styles,
        escape_html(get_element_id(el)),
        data_id_attr,
        class_attr,
        src,
        alt_attr,
        style_attr,
        event_attrs
    )
}

fn render_input(el: &ElementDef) -> String {
    let mut styles = vec![
        "padding: 8px 12px".to_string(),
        "border: 1px solid #555".to_string(),
        "border-radius: 4px".to_string(),
        "background: #2a2a3a".to_string(),
        "color: white".to_string(),
        "font-size: 14px".to_string(),
        "outline: none".to_string(),
    ];

    if let Some(w) = el.width {
        styles.push(format!("width: {}px", w));
    }
    if let Some(h) = el.height {
        styles.push(format!("height: {}px", h));
    }
    if let Some(ref bg) = el.background_color {
        styles.retain(|s| !s.starts_with("background:"));
        styles.push(format!("background: {}", bg));
    }
    if let Some(ref tc) = el.text_color {
        styles.retain(|s| !s.starts_with("color:"));
        styles.push(format!("color: {}", tc));
    }
    if let Some(br_style) = build_border_radius_style(el) {
        styles.retain(|s| !s.starts_with("border-radius:"));
        styles.push(br_style);
    } else if let Some(br) = el.border_radius {
        styles.retain(|s| !s.starts_with("border-radius:"));
        styles.push(format!("border-radius: {}px", br));
    }
    if let Some(p) = el.padding {
        styles.retain(|s| !s.starts_with("padding:"));
        styles.push(format!("padding: {}px", p));
    }

    let side_border_styles = build_border_sides_styles(el);
    if !side_border_styles.is_empty() {
        styles.retain(|s| !s.starts_with("border:"));
        styles.extend(side_border_styles);
    } else if let Some(bw) = el.border_width {
        styles.retain(|s| !s.starts_with("border:"));
        let bc = el.border_color.as_deref().unwrap_or("#555");
        styles.push(format!("border: {}px solid {}", bw, bc));
    }

    if let Some(ref cursor) = el.cursor {
        styles.push(format!("cursor: {}", cursor));
    }
    if let Some(ref transition) = el.transition {
        styles.push(format!("transition: {}", transition));
    }

    let style_attr = format!(" style=\"{}\"", styles.join("; "));

    let oninput_attr = if let Some(ref cb_id) = el.on_input {
        format!(" oninput=\"handleInput('{}', this.value)\"", escape_html(cb_id))
    } else {
        String::new()
    };

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let data_id_attr = build_data_id_attr(el);

    let value_attr = el.value.as_ref()
        .map(|v| format!(" value=\"{}\"", escape_html(v)))
        .unwrap_or_default();

    let placeholder_attr = el.placeholder.as_ref()
        .map(|p| format!(" placeholder=\"{}\"", escape_html(p)))
        .unwrap_or_default();

    let class_attr = if el.class_names.is_empty() {
        String::new()
    } else {
        format!(" class=\"{}\"", el.class_names.join(" "))
    };

    format!(
        "{}<input id=\"{}\"{}{}type=\"text\"{}{}{}{}{}/>",
        state_styles,
        escape_html(get_element_id(el)),
        data_id_attr,
        class_attr,
        style_attr,
        oninput_attr,
        event_attrs,
        value_attr,
        placeholder_attr
    )
}

fn render_checkbox(el: &ElementDef) -> String {
    let checked_attr = if el.checked.unwrap_or(false) { " checked" } else { "" };

    let onchange_attr = if let Some(ref cb_id) = el.on_change {
        format!(" onchange=\"handleChange('{}', this.checked)\"", escape_html(cb_id))
    } else {
        String::new()
    };

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let data_id_attr = build_data_id_attr(el);

    let label_html = el.label.as_ref()
        .map(|l| format!("<span style=\"margin-left: 8px\">{}</span>", escape_html(l)))
        .unwrap_or_default();

    let class_attr = if el.class_names.is_empty() {
        String::new()
    } else {
        format!(" class=\"{}\"", el.class_names.join(" "))
    };

    let accent_color = el.background_color.as_deref().unwrap_or("#3b82f6");
    let cursor_style = el.cursor.as_deref().unwrap_or("pointer");
    let input_style = format!(
        "width: 18px; height: 18px; accent-color: {}; cursor: {}",
        accent_color,
        cursor_style
    );

    format!(
        "{}<label id=\"{}\"{}{}style=\"display: flex; align-items: center; cursor: {}\"{}><input type=\"checkbox\" style=\"{}\"{}{}/>{}</label>",
        state_styles,
        escape_html(get_element_id(el)),
        data_id_attr,
        class_attr,
        cursor_style,
        event_attrs,
        input_style,
        checked_attr,
        onchange_attr,
        label_html
    )
}

fn render_radio(el: &ElementDef) -> String {
    let checked_attr = if el.checked.unwrap_or(false) { " checked" } else { "" };

    let name_attr = el.radio_group.as_ref()
        .map(|g| format!(" name=\"{}\"", escape_html(g)))
        .unwrap_or_default();

    let value_attr = el.value.as_ref()
        .map(|v| format!(" value=\"{}\"", escape_html(v)))
        .unwrap_or_default();

    let onchange_attr = if let Some(ref cb_id) = el.on_change {
        format!(" onchange=\"handleChange('{}', this.value)\"", escape_html(cb_id))
    } else {
        String::new()
    };

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let data_id_attr = build_data_id_attr(el);

    let label_html = el.label.as_ref()
        .map(|l| format!("<span style=\"margin-left: 8px\">{}</span>", escape_html(l)))
        .unwrap_or_default();

    let class_attr = if el.class_names.is_empty() {
        String::new()
    } else {
        format!(" class=\"{}\"", el.class_names.join(" "))
    };

    let accent_color = el.background_color.as_deref().unwrap_or("#3b82f6");
    let cursor_style = el.cursor.as_deref().unwrap_or("pointer");
    let input_style = format!(
        "width: 18px; height: 18px; accent-color: {}; cursor: {}",
        accent_color,
        cursor_style
    );

    format!(
        "{}<label id=\"{}\"{}{}style=\"display: flex; align-items: center; cursor: {}\"{}><input type=\"radio\" style=\"{}\"{}{}{}{}/>{}</label>",
        state_styles,
        escape_html(get_element_id(el)),
        data_id_attr,
        class_attr,
        cursor_style,
        event_attrs,
        input_style,
        name_attr,
        value_attr,
        checked_attr,
        onchange_attr,
        label_html
    )
}

fn render_select(el: &ElementDef) -> String {
    let mut styles = vec![
        "padding: 8px 12px".to_string(),
        "font-size: 14px".to_string(),
        "cursor: pointer".to_string(),
        "outline: none".to_string(),
    ];

    if let Some(w) = el.width {
        styles.push(format!("width: {}px", w));
    }
    if let Some(ref bg) = el.background_color {
        styles.retain(|s| !s.starts_with("background:"));
        styles.push(format!("background: {}", bg));
    }
    if let Some(ref tc) = el.text_color {
        styles.retain(|s| !s.starts_with("color:"));
        styles.push(format!("color: {}", tc));
    }
    if let Some(br) = el.border_radius {
        styles.retain(|s| !s.starts_with("border-radius:"));
        styles.push(format!("border-radius: {}px", br));
    }
    if let Some(bw) = el.border_width {
        let bc = el.border_color.as_deref().unwrap_or("#333");
        styles.push(format!("border: {}px solid {}", bw, bc));
    }
    if let Some(ref cursor) = el.cursor {
        styles.retain(|s| !s.starts_with("cursor:"));
        styles.push(format!("cursor: {}", cursor));
    }
    if let Some(ref transition) = el.transition {
        styles.push(format!("transition: {}", transition));
    }

    if let Some(ref raw) = el.style {
        styles.push(raw.clone());
    }

    let style_attr = format!(" style=\"{}\"", styles.join("; "));

    let onchange_attr = if let Some(ref cb_id) = el.on_change {
        format!(" onchange=\"handleChange('{}', this.value)\"", escape_html(cb_id))
    } else {
        String::new()
    };

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let data_id_attr = build_data_id_attr(el);

    let options_html: String = el.options.iter().map(|opt| {
        let selected = el.selected.as_ref().map(|s| s == &opt.value).unwrap_or(false);
        let selected_attr = if selected { " selected" } else { "" };
        format!(
            "<option value=\"{}\"{}>{}</option>",
            escape_html(&opt.value),
            selected_attr,
            escape_html(&opt.label)
        )
    }).collect();

    let class_attr = if el.class_names.is_empty() {
        String::new()
    } else {
        format!(" class=\"{}\"", el.class_names.join(" "))
    };

    format!(
        "{}<select id=\"{}\"{}{}{}{}{}>{}</select>",
        state_styles,
        escape_html(get_element_id(el)),
        data_id_attr,
        class_attr,
        style_attr,
        onchange_attr,
        event_attrs,
        options_html
    )
}

fn escape_html(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#39;")
}