import calendar
from datetime import datetime


def hvezdicky_html(pocet):
    return "⭐" * pocet + "☆" * (5 - pocet)


def zobraz_kalendar_obsadenosti(db_data, rok, mesiac):
    obsadene = set()
    for event in db_data:
        if event.get("stav") == "schvalene":
            try:
                d = datetime.strptime(event["datum"], "%Y-%m-%d").date()
                if d.year == rok and d.month == mesiac:
                    obsadene.add(d.day)
            except Exception:
                pass

    cal = calendar.monthcalendar(rok, mesiac)
    nazvy_dni = ["Po", "Ut", "St", "Št", "Pi", "So", "Ne"]

    html = """
    <div style="background: rgba(0,0,0,0.85); border: 2px solid #d4af37; border-radius: 12px; padding: 15px; margin: 10px 0 20px 0;">
      <h4 style="text-align:center; color:#d4af37; margin-bottom:10px;">📅 Obsadenosť termínov (X = obsadené)</h4>
      <table style="width:100%; border-collapse:collapse; text-align:center; color:white;">
        <tr>
    """
    for den in nazvy_dni:
        html += f'<th style="padding:8px; border-bottom:1px solid rgba(212,175,55,0.4); color:#d4af37;">{den}</th>'
    html += "</tr>"

    for tyzden in cal:
        html += "<tr>"
        for den in tyzden:
            if den == 0:
                html += '<td style="padding:10px; color:#555;">&nbsp;</td>'
            elif den in obsadene:
                html += '<td style="padding:10px; font-weight:bold; color:#ff4d4d;">X</td>'
            else:
                html += f'<td style="padding:10px;">{den}</td>'
        html += "</tr>"

    html += """
      </table>
      <div style="text-align:center; margin-top:10px; color:#aaa; font-size:0.9rem;">
        Červené <b>X</b> = termín je už obsadený (schválená akcia)
      </div>
    </div>
    """
    return html
