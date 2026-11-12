import importlib.util
from datetime import date, timedelta
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('calendar_art', ROOT/'scripts/update_contributions.py')
art = importlib.util.module_from_spec(spec)
spec.loader.exec_module(art)


def fixture():
    cells = []
    for i in range(365):
        day = date(2025, 11, 13) + timedelta(days=i)
        cells.append(f'<td class="ContributionCalendar-day" id="d{i}" data-date="{day}" data-level="{1 if i == 0 else 0}"></td><tool-tip for="d{i}">{"1,234 contributions" if i == 0 else "No contributions"} on November 13th.</tool-tip>')
    return ''.join(reversed(cells))  # GitHub HTML is not chronological.


class ContributionsTest(unittest.TestCase):
    def test_parse_real_fields_and_sort(self):
        days = art.parse_days(fixture())
        self.assertEqual(days[0], {'date': '2025-11-13', 'count': 1234, 'level': 1})
        self.assertEqual(len(days), 365)
        self.assertEqual(sum(d['count'] for d in days), 1234)

    def test_reject_incomplete_duplicate_or_unknown_data(self):
        html = fixture()
        for broken in ['', html.replace('data-date="2025-11-14"', 'data-date="2025-11-13"'), html.replace('1,234 contributions', 'Count unavailable'), html.replace('data-level="1"', 'data-level="5"')]:
            with self.subTest(html=broken[:60]), self.assertRaises(ValueError):
                art.parse_days(broken)

    def test_all_variants_preserve_dates_and_levels(self):
        days = art.parse_days(fixture())
        ns = {'s': 'http://www.w3.org/2000/svg'}
        for mobile in [False, True]:
            for dark in [False, True]:
                svg = ET.fromstring(art.render(days, dark, mobile))
                cells = svg.findall('s:rect[@class="day"]', ns)
                self.assertEqual([(c.attrib['data-date'], int(c.attrib['data-level'])) for c in cells], [(d['date'], d['level']) for d in days])
                self.assertIn('We add value, every day', svg.find('s:title', ns).text)
                for cell in cells:
                    self.assertLessEqual(float(cell.attrib['x'])+12, int(svg.attrib['width']))
                    self.assertLessEqual(float(cell.attrib['y'])+12, int(svg.attrib['height']))


if __name__ == '__main__':
    unittest.main()
