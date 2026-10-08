"""Validate profile assets without network calls or dependencies."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class Images(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.images = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.images.append(dict(attrs))

class ProfileTests(unittest.TestCase):
    def test_readme_images_have_accessible_local_assets(self):
        images = Images((ROOT / 'README.md').read_text()).images
        self.assertTrue(images)
        for image in images:
            with self.subTest(image=image['src']):
                self.assertTrue(image.get('alt', '').strip())
                path = (ROOT / image['src']).resolve()
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertTrue(path.is_file())
                svg = ET.parse(path).getroot()
                self.assertEqual(int(svg.attrib['width']), int(image['width']))
                self.assertEqual(int(svg.attrib['height']), int(image['height']))

    def test_assets_are_self_contained_accessible_svg(self):
        for path in (ROOT / 'assets').rglob('*.svg'):
            with self.subTest(path=path.name):
                svg = ET.parse(path).getroot()
                self.assertEqual(svg.attrib.get('role'), 'img')
                self.assertTrue(svg.find('{http://www.w3.org/2000/svg}title').text)
                self.assertGreater(float(svg.attrib['width']), 0)
                self.assertGreater(float(svg.attrib['height']), 0)
                ids = {node.attrib['id'] for node in svg.iter() if 'id' in node.attrib}
                for label in svg.attrib['aria-labelledby'].split():
                    self.assertIn(label, ids)
                source = path.read_text()
                self.assertNotRegex(source, r'(?i)url\s*\(|@import|@font-face')
                for node in svg.iter():
                    self.assertNotIn(node.tag.rsplit('}', 1)[-1], ['script', 'foreignObject', 'image'])
                    for attr in node.attrib:
                        self.assertFalse(attr.rsplit('}', 1)[-1].startswith('on'))
                        self.assertNotEqual(attr.rsplit('}', 1)[-1], 'href')

    def test_intro_has_finite_timeline_and_motion_alternative(self):
        svg = ET.parse(ROOT / 'assets/intro.svg').getroot()
        messages = [node for node in svg.iter()
                    if 'message' in node.attrib.get('class', '').split()]
        self.assertEqual(len(messages), 3)
        style = svg.find('{http://www.w3.org/2000/svg}style').text
        self.assertNotIn('infinite', style)
        delays = [float(value) for value in re.findall(
            r'\.message-\d+\s*\{\s*animation-delay:\s*([\d.]+)s', style)]
        duration = float(re.search(r'animation:\s*reveal\s+([\d.]+)s', style)[1])
        self.assertEqual(len(delays), len(messages))
        self.assertLessEqual(max(delays) + duration, 5)
        reduced = style.split('@media (prefers-reduced-motion: reduce)', 1)[1]
        self.assertRegex(reduced, r'\.message\s*\{[^}]*animation: none;[^}]*opacity: 1;')
        self.assertRegex(reduced, r'\.typing\s*\{[^}]*animation: none;[^}]*opacity: 0;')

    def test_capability_text_and_work_disclosure_are_present(self):
        text = (ROOT / 'README.md').read_text()
        for capability in ['RAG']:
            self.assertIn(capability, text)
            self.assertNotIn(f'badges/{capability.lower()}.svg', text)
        self.assertIn('Source code and demos for these professional systems are not public.', text)

    def test_tools_have_twelve_unique_local_32px_badges(self):
        text = (ROOT / 'README.md').read_text()
        section = text.split('## Tools and capabilities', 1)[1].split('<details>', 1)[0]
        images = Images(section).images
        self.assertEqual(len(images), 12)
        self.assertEqual(len({image['src'] for image in images}), 12)
        for image in images:
            with self.subTest(image=image['src']):
                self.assertTrue(image['src'].startswith('assets/badges/'))
                self.assertEqual(image['height'], '32')
                self.assertGreater(int(image['width']), 0)

if __name__ == '__main__':
    unittest.main()
