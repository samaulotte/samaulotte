"""Render the public GitHub calendar. Standard library only; no token required."""
import argparse
import base64
import calendar
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://github.com/users/samaulotte/contributions'


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = []
        self.tooltips = {}
        self.tooltip = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'ContributionCalendar-day' in attrs.get('class', '').split() and attrs.get('data-date'):
            self.cells.append(attrs)
        if tag == 'tool-tip':
            self.tooltip = attrs.get('for')
            if self.tooltip in self.tooltips:
                raise ValueError('Duplicate contribution tooltip')
            if self.tooltip:
                self.tooltips[self.tooltip] = ''

    def handle_data(self, value):
        if self.tooltip:
            self.tooltips[self.tooltip] += value

    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tooltip = None


def parse_days(html):
    parser = CalendarParser()
    parser.feed(html)
    days = []
    for cell in parser.cells:
        day = date.fromisoformat(cell['data-date'])
        level = int(cell['data-level'])
        tooltip = parser.tooltips.get(cell.get('id'), '').strip()
        count_match = re.match(r'(\d[\d,]*) contributions? on ', tooltip)
        if tooltip.startswith('No contributions on '):
            count = 0
        elif count_match:
            count = int(count_match[1].replace(',', ''))
        else:
            raise ValueError(f'Unknown contribution count for {day}: {tooltip!r}')
        if not 0 <= level <= 4 or (count == 0) != (level == 0):
            raise ValueError(f'Invalid contribution level for {day}')
        days.append({'date': day.isoformat(), 'count': count, 'level': level})
    days.sort(key=lambda day: day['date'])
    if not 350 <= len(days) <= 371:
        raise ValueError('Expected one complete public contribution year')
    for previous, current in zip(days, days[1:]):
        if date.fromisoformat(current['date']) - date.fromisoformat(previous['date']) != timedelta(days=1):
            raise ValueError('Duplicate or missing contribution dates')
    return days


def render(days, dark=False, mobile=False):
    bg, fg, muted = ('#171b22', '#f1f3f7', '#b5bbc8') if dark else ('#f3f3f1', '#17191d', '#5d606a')
    colors = ['#303641', '#354b8b', '#536cc4', '#8297ef', '#b2c2ff'] if dark else ['#e3e5e9', '#c3ceff', '#94a7ff', '#627fff', '#284be8']
    blue = '#9db2ff' if dark else '#2549ef'
    width, height = (480, 440) if mobile else (880, 276)
    css = ''.join('@font-face{font-family:' + family + ';src:url(data:font/ttf;base64,' + base64.b64encode((ROOT/'fonts'/file).read_bytes()).decode() + ')}' for family, file in [('Editorial', 'InstrumentSerif-Regular.ttf'), ('Italic', 'InstrumentSerif-Italic.ttf')])
    first, last = date.fromisoformat(days[0]['date']), date.fromisoformat(days[-1]['date'])
    start = first - timedelta(days=(first.weekday()+1) % 7)
    total = sum(day['count'] for day in days)
    title = f'We add value, every day — {total} GitHub contributions visible on the public profile, {first} to {last}.'
    body = [f'<rect width="{width}" height="{height}" rx="16" fill="{bg}"/>']
    x = 30 if mobile else 44
    body.append(f'<text x="{x}" y="61" font-family="Editorial" font-size="38" fill="{fg}">We add value, <tspan font-family="Italic" fill="{blue}">every day</tspan></text>')

    def label(x, y, text, size=11, anchor='start'):
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="monospace" font-size="{size}" fill="{muted}">{escape(text)}</text>'

    updated = f'UPDATED {last.day:02d} {calendar.month_abbr[last.month].upper()} {last.year}'
    body.append(label(x if mobile else 836, 87 if mobile else 59, updated, 10, 'start' if mobile else 'end'))
    months = set()
    for day in days:
        day_date = date.fromisoformat(day['date'])
        offset = (day_date-start).days
        week, weekday = divmod(offset, 7)
        panel, column = divmod(week, 27) if mobile else (0, week)
        pitch = 15.5 if mobile else 14.65
        px, py = x + column*pitch, (115 if mobile else 101) + panel*143 + weekday*(14 if mobile else 14)
        body.append(f'<rect class="day" data-date="{day_date}" data-level="{day["level"]}" x="{px:.2f}" y="{py}" width="12" height="12" rx="3" fill="{colors[day["level"]]}"><title>{day_date}: {day["count"]} contributions</title></rect>')
        key = (panel, day_date.year, day_date.month)
        # Label the first Sunday of a month, avoiding clipped partial months.
        if weekday == 0 and day_date.day <= 7 and key not in months:
            body.append(label(round(px, 2), (230+panel*143) if mobile else 218, calendar.month_abbr[day_date.month], 10))
            months.add(key)
    legend_x, legend_y = (309, 405) if mobile else (695, 244)
    body.append(label(legend_x-10, legend_y+9, 'less', 10, 'end'))
    for i, color in enumerate(colors):
        body.append(f'<rect x="{legend_x+i*15}" y="{legend_y}" width="12" height="12" rx="3" fill="{color}"/>')
    body.append(label(legend_x+81, legend_y+9, 'more', 10))
    body.append(label(x, legend_y+9, 'PUBLIC GITHUB ACTIVITY', 9))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><style>{css}</style>{"".join(body)}</svg>\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, help='Use a saved public HTML response for offline validation')
    args = parser.parse_args()
    if args.html:
        html = args.html.read_text()
    else:
        request = Request(URL, headers={'User-Agent': 'samaulotte-profile-calendar/1.0', 'Accept-Language': 'en-US'})
        with urlopen(request, timeout=30) as response:
            html = response.read(2_000_001).decode('utf-8')
        if len(html) > 2_000_000:
            raise ValueError('Unexpectedly large public calendar response')
    days = parse_days(html)
    # Complete parsing and rendering before overwriting the last successful snapshot.
    outputs = {f'contributions-{theme}{suffix}.svg': render(days, dark, mobile) for theme, dark in [('light', False), ('dark', True)] for suffix, mobile in [('', False), ('-mobile', True)]}
    target = ROOT/'contributions'
    target.mkdir(exist_ok=True)
    for name, content in outputs.items():
        (target/name).write_text(content)
    data = {'source': URL, 'range': {'start': days[0]['date'], 'end': days[-1]['date']}, 'total': sum(day['count'] for day in days), 'days': days}
    (target/'data.json').write_text(json.dumps(data, indent=2)+'\n')
    print(f'{len(days)} days, {data["total"]} publicly visible contributions, {data["range"]}')


if __name__ == '__main__':
    main()
