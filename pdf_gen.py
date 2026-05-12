from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from io import BytesIO
from datetime import datetime, timedelta

PAGE_W, PAGE_H = 612, 792
LEFT = 13.6
RIGHT = 586.4

FONT       = "Helvetica"
FONT_BOLD  = "Helvetica-Bold"
FONT_SIZE  = 8

# Watermark color — light gray matching the original
WM_COLOR = Color(0.75, 0.75, 0.75, alpha=0.45)


def y(plumber_top, size=FONT_SIZE):
    return PAGE_H - plumber_top - size + 2


def section_height(n_subjects):
    base = 9.9 + 8 + 12.5 + 8 + 4.3 + 8 + 16.5 + 8 + 9.3 + 8 + 9.1 + 8 + 8.2
    return base + max(0, n_subjects - 1) * 13.5


STUDENT_BOX_HEIGHT = 50.1
PAGE_BOTTOM        = 752
CONTENT_START_Y    = 84.8
NEXT_PAGE_START_Y  = 78.0


def draw_watermark(c):
    """Draw 'DOCUMENTO NO OFICIAL' watermark diagonally across the page."""
    c.saveState()
    c.setFillColor(WM_COLOR)
    c.setFont(FONT_BOLD, 54)
    # Rotate and center the text diagonally
    c.translate(PAGE_W / 2, PAGE_H / 2)
    c.rotate(45)
    c.drawCentredString(0, 20, "DOCUMENTO")
    c.drawCentredString(0, -40, "NO OFICIAL")
    c.restoreState()


def draw_header(c, page_num, total_pages, print_date):
    # Line 1: Bold (matches original)
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(17.8, y(48.4), "Instituto Tecnológico de Santo Domingo")
    c.drawString(398.3, y(48.4), "Fecha de Impresión:")
    c.drawString(486.9, y(48.4), print_date)

    # Line 2: Regular (matches original)
    c.setFont(FONT, FONT_SIZE)
    c.drawString(17.8, y(57.7), "Dirección de Registro")
    c.drawString(447.2, y(57.7), "Página:")
    c.drawString(486.9, y(57.7), f"{page_num} de {total_pages}")

    # Line 3: Regular (matches original — NOT bold)
    c.drawString(17.8, y(67.2), "Historial Académico Estudiantil")


def draw_student_box(c, data, top_y=84.8):
    bot_y = top_y + STUDENT_BOX_HEIGHT
    rl_bot = PAGE_H - bot_y
    rl_h   = bot_y - top_y

    c.rect(LEFT, rl_bot, RIGHT - LEFT, rl_h)

    rows = [
        ("ID",        data.get("id", ""),
         "Créditos Convalidados", str(data.get("cred_convalidados", ""))),
        ("Matrícula",  data.get("matricula", ""),
         "Créditos Aprobados",    str(data.get("cred_aprobados", ""))),
        ("Nombre",     data.get("nombre", ""),
         "Créditos Programa",     str(data.get("cred_programa", ""))),
        ("Programa",   data.get("programa", ""),
         "Asignaturas Aprobadas", f"{data.get('asig_aprobadas', '')} / {data.get('asig_total', '')}"),
        ("Cond. Ac",   data.get("cond_ac", ""),
         "Estatus",               data.get("estatus", "")),
    ]

    row_tops = [86.4, 96.0, 105.5, 115.0, 124.5]
    for (ll, lv, rl_label, rv), row_top in zip(rows, row_tops):
        base_y = y(row_top)

        # Left label: Regular
        c.setFont(FONT, FONT_SIZE)
        c.drawString(19.2, base_y, ll)
        # Colon and value: Bold
        c.setFont(FONT_BOLD, FONT_SIZE)
        c.drawString(91.5, base_y, ":")
        c.drawString(96.3, base_y, lv)

        # Right label: Regular
        c.setFont(FONT, FONT_SIZE)
        c.drawString(358.4, base_y, rl_label)
        # Colon and value: Bold
        c.setFont(FONT_BOLD, FONT_SIZE)
        c.drawString(470.9, base_y, ":")
        c.drawString(475.8, base_y, rv)


def draw_trimester(c, trim, box_top):
    n = len(trim["subjects"])
    h = section_height(n)
    box_bot = box_top + h
    rl_bot = PAGE_H - box_bot

    c.rect(LEFT, rl_bot, RIGHT - LEFT, h)

    # Section title — Bold
    title_top = box_top + 9.9
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(19.2, y(title_top), trim["periodo"])

    # Column headers — Bold
    hdr_top = title_top + 8 + 12.5
    c.drawString(31.0,  y(hdr_top), "Clave")
    c.drawString(84.5,  y(hdr_top), "Sec")
    c.drawString(119.0, y(hdr_top), "Nombre de la Asignatura:")
    c.drawString(442.3, y(hdr_top), "Calif.")
    c.drawString(491.3, y(hdr_top), "CR")
    c.drawString(539.3, y(hdr_top), "Puntos")
    c.setFont(FONT, FONT_SIZE)

    # Subject rows — Regular
    row_top = hdr_top + 8 + 4.3
    total_cr = 0
    total_pts = 0.0
    EXCLUDED_GRADES = {"CO", "R", "EI", "AP"}

    for i, subj in enumerate(trim["subjects"]):
        rt = row_top + i * 13.5
        base = y(rt)
        c.drawCentredString(40, base, subj.get("clave", ""))
        c.drawString(87.0,  base, subj.get("sec", ""))
        c.drawString(119.0, base, subj.get("nombre", ""))
        calif = subj.get("calif", "")
        c.drawString(446.0, base, calif)
        cr_val = subj.get("cr", "")
        c.drawRightString(500, base, str(cr_val))
        pts_val = subj.get("puntos", "0,0")
        c.drawRightString(560, base, str(pts_val))

        if calif.upper() not in EXCLUDED_GRADES:
            try:
                total_cr += int(cr_val)
            except (ValueError, TypeError):
                pass
            try:
                total_pts += float(str(pts_val).replace(",", "."))
            except (ValueError, TypeError):
                pass

    total_pts = round(total_pts, 2)

    # Underlines above totals
    last_row_bot = row_top + max(0, n - 1) * 13.5 + 8
    underline_y_pl = last_row_bot + 8.6
    ul_rl = PAGE_H - underline_y_pl
    c.setLineWidth(0.5)
    c.line(476.7, ul_rl, 514.2, ul_rl)
    c.line(532.3, ul_rl, 569.8, ul_rl)
    c.setLineWidth(1)

    # Totals row — Regular
    totals_top = underline_y_pl + 7.9
    c.drawRightString(500, y(totals_top), str(total_cr))
    pts_str = f"{total_pts:.2f}".replace(".", ",")
    c.drawRightString(560, y(totals_top), pts_str)

    # Condición Académica / Índice Trimestral
    cond_top = totals_top + 8 + 9.3
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(21.4, y(cond_top), "Condición Académica:")
    c.setFont(FONT, FONT_SIZE)
    c.drawString(131.7, y(cond_top), trim.get("condicion", ""))
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(358.4, y(cond_top), "Índice Trimestral:")
    c.setFont(FONT, FONT_SIZE)
    c.drawString(493.4, y(cond_top), trim.get("indice_trimestral", ""))

    # Descripción / Índice Acumulado
    desc_top = cond_top + 8 + 9.1
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(21.4, y(desc_top), "Descripción Observación:")
    c.setFont(FONT, FONT_SIZE)
    c.drawString(131.7, y(desc_top), trim.get("descripcion", ""))
    c.setFont(FONT_BOLD, FONT_SIZE)
    c.drawString(358.4, y(desc_top), "Índice Acumulado:")
    c.setFont(FONT, FONT_SIZE)
    c.drawString(493.4, y(desc_top), trim.get("indice_acumulado", ""))

    return box_bot


def count_pages(trimesters):
    """Count content pages (excluding trailing blank page)."""
    cur_y = CONTENT_START_Y + STUDENT_BOX_HEIGHT
    pages = 1
    for trim in trimesters:
        h = section_height(len(trim["subjects"]))
        if cur_y + h > PAGE_BOTTOM:
            pages += 1
            cur_y = NEXT_PAGE_START_Y
        cur_y += h
    return pages


def generate_pdf(student_data, trimesters):
    buf = BytesIO()

    # +3.5 hours offset and original date format (no leading zeros)
    now = datetime.now() + timedelta(hours=3, minutes=30)
    print_date = f"{now.day}/{now.month}/{now.year} {now.strftime('%H:%M')} PM"

    content_pages = count_pages(trimesters)
    total_pages = content_pages + 1  # +1 for trailing blank page

    c = canvas.Canvas(buf, pagesize=letter)
    c.setLineWidth(0.5)

    current_page = 1
    draw_header(c, current_page, total_pages, print_date)
    draw_watermark(c)
    draw_student_box(c, student_data)

    cur_y = CONTENT_START_Y + STUDENT_BOX_HEIGHT

    for trim in trimesters:
        h = section_height(len(trim["subjects"]))
        if cur_y + h > PAGE_BOTTOM:
            c.showPage()
            current_page += 1
            c.setLineWidth(0.5)
            draw_header(c, current_page, total_pages, print_date)
            draw_watermark(c)
            cur_y = NEXT_PAGE_START_Y
        draw_trimester(c, trim, cur_y)
        cur_y += h

    # Trailing blank page with header and watermark only
    c.showPage()
    current_page += 1
    c.setLineWidth(0.5)
    draw_header(c, current_page, total_pages, print_date)
    draw_watermark(c)

    c.save()
    buf.seek(0)
    return buf.read()
