"""
Selenium tests for NNTMapper — Meta-Analytic NNT Calculator.

Usage:
    python -m pytest tests/test_nntmapper.py -v --timeout=60
"""

import sys
import os
import time
import unittest
import math

if __name__ == '__main__' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

HTML_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nntmapper.html'))
FILE_URL = 'file:///' + HTML_PATH.replace('\\', '/')

_WDM_CACHE_ROOT = os.path.expanduser('~/.wdm/drivers/chromedriver/win64')
_CACHED_DRIVERS = []
if os.path.isdir(_WDM_CACHE_ROOT):
    for _ver in sorted(os.listdir(_WDM_CACHE_ROOT), reverse=True):
        for _subdir in ('chromedriver-win32', ''):
            _candidate = os.path.join(_WDM_CACHE_ROOT, _ver, _subdir, 'chromedriver.exe').rstrip(os.sep)
            if os.path.isfile(_candidate):
                _CACHED_DRIVERS.append(_candidate)
                break


def _chrome_options():
    opts = ChromeOptions()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--incognito')
    opts.add_argument('--window-size=1280,900')
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    return opts


def _get_driver():
    opts = _chrome_options()
    for driver_path in _CACHED_DRIVERS:
        try:
            return webdriver.Chrome(service=ChromeService(executable_path=driver_path), options=opts)
        except WebDriverException:
            continue
    try:
        return webdriver.Chrome(options=opts)
    except WebDriverException:
        pass
    try:
        from selenium.webdriver.edge.options import Options as EdgeOptions
        eopts = EdgeOptions()
        eopts.add_argument('--headless=new')
        eopts.add_argument('--no-sandbox')
        eopts.add_argument('--disable-gpu')
        eopts.add_argument('--inprivate')
        eopts.add_argument('--window-size=1280,900')
        return webdriver.Edge(options=eopts)
    except WebDriverException:
        pass
    raise WebDriverException('No working WebDriver found.')


class TestNNTMapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = _get_driver()
        cls.driver.set_page_load_timeout(30)
        cls.driver.get(FILE_URL)
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            try:
                import threading
                done = threading.Event()
                def _q():
                    try: cls.driver.quit()
                    except: pass
                    finally: done.set()
                t = threading.Thread(target=_q, daemon=True)
                t.start()
                if not done.wait(10):
                    try: cls.driver.service.process.kill()
                    except: pass
            except: pass

    def _js(self, script):
        return self.driver.execute_script(script)

    # ── 01: Page Title ───────────────────────────────────────────

    def test_01_page_title(self):
        self.assertIn('NNTMapper', self.driver.title)

    # ── 02: Header elements ──────────────────────────────────────

    def test_02_header_buttons(self):
        about = self.driver.find_element(By.ID, 'aboutBtn')
        dark = self.driver.find_element(By.ID, 'darkModeBtn')
        self.assertTrue(about.is_displayed())
        self.assertTrue(dark.is_displayed())

    # ── 03: Auto-compute on load ─────────────────────────────────

    def test_03_auto_compute_on_load(self):
        """Default SGLT2i example should auto-compute NNT on load."""
        nnt_text = self.driver.find_element(By.ID, 'nntValue').text
        self.assertNotEqual(nnt_text, '—', 'NNT should compute on page load')
        self.assertNotIn('Invalid', nnt_text)

    # ── 04: NNT value for SGLT2i default ─────────────────────────

    def test_04_nnt_value_sglt2i(self):
        """SGLT2i OR=0.74, CER=20% should give NNT ~15-20."""
        nnt = self._js("return window._lastResult ? window._lastResult.nnt : null;")
        self.assertIsNotNone(nnt)
        self.assertGreater(nnt, 5, f'NNT should be > 5, got {nnt}')
        self.assertLess(nnt, 30, f'NNT should be < 30, got {nnt}')

    # ── 05: Load statins example ─────────────────────────────────

    def test_05_load_statins_example(self):
        self._js("""
            document.getElementById('exampleSelect').value = 'statins';
            document.getElementById('exampleSelect').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        measure = self._js("return document.getElementById('effectMeasure').value;")
        self.assertEqual(measure, 'RR')
        est = self._js("return parseFloat(document.getElementById('effectEst').value);")
        self.assertAlmostEqual(est, 0.75, places=2)
        # NNT for statins at 5% baseline should be high (50-100+)
        nnt = self._js("return window._lastResult ? window._lastResult.nnt : null;")
        self.assertIsNotNone(nnt)
        self.assertGreater(nnt, 30, f'Statins NNT at 5% baseline should be >30, got {nnt}')

    # ── 06: Load aspirin example ─────────────────────────────────

    def test_06_load_aspirin_example(self):
        self._js("""
            document.getElementById('exampleSelect').value = 'aspirin';
            document.getElementById('exampleSelect').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        nnt = self._js("return window._lastResult ? window._lastResult.nnt : null;")
        self.assertIsNotNone(nnt)
        # Aspirin RR=0.80, CER=8% → ARR=1.6% → NNT≈63
        self.assertGreater(nnt, 30)
        self.assertLess(nnt, 120)

    # ── 07: Slider changes NNT ───────────────────────────────────

    def test_07_slider_changes_nnt(self):
        """Changing baseline risk slider should update NNT."""
        # Reset to SGLT2i
        self._js("""
            document.getElementById('exampleSelect').value = 'sglt2i';
            document.getElementById('exampleSelect').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.3)
        nnt_at_20 = self._js("return window._lastResult.nnt;")

        # Move slider to 5%
        self._js("""
            var s = document.getElementById('baselineRisk');
            s.value = '5';
            s.dispatchEvent(new Event('input'));
        """)
        time.sleep(0.3)
        nnt_at_5 = self._js("return window._lastResult.nnt;")

        # Lower baseline risk → higher NNT
        self.assertGreater(nnt_at_5, nnt_at_20,
            f'NNT at 5% ({nnt_at_5}) should be > NNT at 20% ({nnt_at_20})')

    # ── 08: Dark mode toggle ─────────────────────────────────────

    def test_08_dark_mode(self):
        btn = self.driver.find_element(By.ID, 'darkModeBtn')
        btn.click()
        time.sleep(0.3)
        theme = self.driver.find_element(By.TAG_NAME, 'html').get_attribute('data-theme')
        self.assertEqual(theme, 'dark')
        btn.click()
        time.sleep(0.3)

    # ── 09: About modal ──────────────────────────────────────────

    def test_09_about_modal(self):
        self.driver.find_element(By.ID, 'aboutBtn').click()
        time.sleep(0.3)
        modal = self.driver.find_element(By.ID, 'aboutModal')
        self.assertNotIn('hidden', modal.get_attribute('class'))
        self.assertIn('NNTMapper', modal.text)
        self.driver.find_element(By.ID, 'aboutClose').click()
        time.sleep(0.3)
        self.assertIn('hidden', self.driver.find_element(By.ID, 'aboutModal').get_attribute('class'))

    # ── 10: No console errors ────────────────────────────────────

    def test_10_no_console_errors(self):
        try:
            logs = self.driver.get_log('browser')
        except Exception:
            self.skipTest('Log capture not supported')
        severe = [e for e in logs if e.get('level') == 'SEVERE' and 'favicon' not in e.get('message', '').lower()]
        if severe:
            self.fail(f'Console errors: {[e["message"] for e in severe]}')

    # ── 11: ARR computation ──────────────────────────────────────

    def test_11_arr_displayed(self):
        arr = self.driver.find_element(By.ID, 'arrVal').text
        self.assertNotEqual(arr, '—')
        self.assertIn('%', arr)

    # ── 12: Prediction interval displayed ────────────────────────

    def test_12_prediction_interval(self):
        pi = self.driver.find_element(By.ID, 'piNNT').text
        self.assertNotEqual(pi, '—')
        self.assertIn('–', pi, 'PI should show a range with dash separator')

    # ── 13: Events prevented ─────────────────────────────────────

    def test_13_events_prevented(self):
        val = self.driver.find_element(By.ID, 'eventsPreventedVal').text
        self.assertNotEqual(val, '—')

    # ── 14: GRADE certainty ──────────────────────────────────────

    def test_14_certainty(self):
        val = self.driver.find_element(By.ID, 'certaintyVal').text
        self.assertIn(val, ['High', 'Moderate', 'Low', 'Very Low'])

    # ── 15: NNT gauge color ──────────────────────────────────────

    def test_15_gauge_color(self):
        gauge = self.driver.find_element(By.ID, 'nntGauge')
        classes = gauge.get_attribute('class')
        has_color = 'green' in classes or 'amber' in classes or 'red' in classes
        self.assertTrue(has_color, f'Gauge should have a color class, got: {classes}')

    # ── 16: Charts rendered ──────────────────────────────────────

    def test_16_charts_rendered(self):
        nnt_chart = self.driver.find_element(By.ID, 'nntCurveChart')
        dc_chart = self.driver.find_element(By.ID, 'decisionCurveChart')
        # Plotly injects SVG elements
        nnt_svg = nnt_chart.find_elements(By.CSS_SELECTOR, '.plot-container, svg')
        dc_svg = dc_chart.find_elements(By.CSS_SELECTOR, '.plot-container, svg')
        self.assertGreater(len(nnt_svg), 0, 'NNT curve chart should have Plotly content')
        self.assertGreater(len(dc_svg), 0, 'Decision curve chart should have Plotly content')

    # ── 17: NNT formula correctness (OR) ─────────────────────────

    def test_17_nnt_formula_or(self):
        """Verify OR → NNT formula against hand calculation."""
        result = self._js("""
            var r = computeNNT('OR', 0.74, 0.20);
            return {arr: r.arr, nnt: r.nnt, eer: r.eer};
        """)
        # Manual: EER = 0.20*0.74 / (1-0.20+0.20*0.74) = 0.148/0.948 = 0.15612
        # ARR = 0.20 - 0.15612 = 0.04388 → NNT = 22.8
        expected_eer = 0.20 * 0.74 / (1 - 0.20 + 0.20 * 0.74)
        expected_arr = 0.20 - expected_eer
        self.assertAlmostEqual(result['eer'], expected_eer, places=4)
        self.assertAlmostEqual(result['arr'], expected_arr, places=4)
        self.assertAlmostEqual(result['nnt'], 1 / expected_arr, places=1)

    # ── 18: NNT formula correctness (RR) ─────────────────────────

    def test_18_nnt_formula_rr(self):
        result = self._js("""
            var r = computeNNT('RR', 0.75, 0.10);
            return {arr: r.arr, nnt: r.nnt};
        """)
        # ARR = 0.10 * (1 - 0.75) = 0.025 → NNT = 40
        self.assertAlmostEqual(result['arr'], 0.025, places=4)
        self.assertAlmostEqual(result['nnt'], 40.0, places=1)

    # ── 19: NNT formula correctness (HR) ─────────────────────────

    def test_19_nnt_formula_hr(self):
        result = self._js("""
            var r = computeNNT('HR', 0.80, 0.15);
            return {arr: r.arr, nnt: r.nnt, eer: r.eer};
        """)
        # EER = 1 - (1-0.15)^0.80 = 1 - 0.85^0.80
        expected_eer = 1 - pow(0.85, 0.80)
        expected_arr = 0.15 - expected_eer
        self.assertAlmostEqual(result['eer'], expected_eer, places=4)
        self.assertAlmostEqual(result['arr'], expected_arr, places=4)

    # ── 20: Edge case — effect = 1.0 (no benefit) ───────────────

    def test_20_no_benefit(self):
        result = self._js("""
            var r = computeNNT('RR', 1.0, 0.10);
            return {arr: r.arr, nnt: r.nnt, isInf: !isFinite(r.nnt)};
        """)
        self.assertAlmostEqual(result['arr'], 0.0, places=6)
        self.assertTrue(result['isInf'], 'NNT should be Infinity when ARR=0')

    # ── 21: Edge case — harmful effect (OR > 1) ─────────────────

    def test_21_harmful_effect(self):
        result = self._js("""
            var r = computeNNT('OR', 1.5, 0.10);
            return {arr: r.arr, isHarmful: r.isHarmful};
        """)
        self.assertTrue(result['isHarmful'], 'OR > 1 should be flagged as harmful')
        self.assertLess(result['arr'], 0, 'ARR should be negative when harmful')

    # ── 22: TruthCert export function exists ─────────────────────

    def test_22_export_function(self):
        result = self._js("return typeof exportBundle === 'function';")
        self.assertTrue(result)

    # ── 23: Skip-nav link ────────────────────────────────────────

    def test_23_skip_nav(self):
        skip = self.driver.find_elements(By.CSS_SELECTOR, 'a[href="#main-content"]')
        self.assertEqual(len(skip), 1, 'Should have exactly one skip-nav link')
        main = self.driver.find_elements(By.ID, 'main-content')
        self.assertEqual(len(main), 1, 'main-content target must exist')

    # ── 24: CSP meta tag ─────────────────────────────────────────

    def test_24_csp_present(self):
        csp = self._js("""
            var m = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
            return m ? m.getAttribute('content') : null;
        """)
        self.assertIsNotNone(csp)
        self.assertIn('default-src', csp)

    # ── 25: Aria-live on results panel ───────────────────────────

    def test_25_aria_live(self):
        panel = self.driver.find_element(By.ID, 'resultsPanel')
        self.assertEqual(panel.get_attribute('aria-live'), 'polite')

    # ── 26: Slider aria attributes ───────────────────────────────

    def test_26_slider_aria(self):
        slider = self.driver.find_element(By.ID, 'baselineRisk')
        self.assertEqual(slider.get_attribute('role'), 'slider')
        self.assertEqual(slider.get_attribute('aria-valuemin'), '1')
        self.assertEqual(slider.get_attribute('aria-valuemax'), '50')

    # ── 27: Custom input compute ─────────────────────────────────

    def test_27_custom_input(self):
        """Setting custom values and clicking compute should work."""
        self._js("""
            document.getElementById('exampleSelect').value = '';
            document.getElementById('effectMeasure').value = 'RR';
            document.getElementById('effectEst').value = '0.60';
            document.getElementById('effectLo').value = '0.50';
            document.getElementById('effectHi').value = '0.72';
            document.getElementById('i2').value = '15';
            document.getElementById('tau2').value = '0.01';
            document.getElementById('kStudies').value = '5';
            document.getElementById('baselineRisk').value = '10';
            compute();
        """)
        time.sleep(0.3)
        nnt = self._js("return window._lastResult ? window._lastResult.nnt : null;")
        self.assertIsNotNone(nnt)
        # RR=0.60, CER=10% → ARR=4% → NNT=25
        self.assertGreater(nnt, 15)
        self.assertLess(nnt, 40)

    # ── 28: Prediction interval widens with heterogeneity ────────

    def test_28_pi_widens_with_tau2(self):
        """Higher tau² should widen the effect-scale prediction interval."""
        # Use strong effect + high baseline so PI stays on same side of null
        self._js("""
            document.getElementById('effectMeasure').value = 'RR';
            document.getElementById('effectEst').value = '0.50';
            document.getElementById('effectLo').value = '0.40';
            document.getElementById('effectHi').value = '0.62';
            document.getElementById('i2').value = '0';
            document.getElementById('kStudies').value = '10';
            document.getElementById('baselineRisk').value = '30';
            document.getElementById('popSize').value = '10000';
            document.getElementById('costPerTx').value = '10000';
        """)

        # tau² = 0
        self._js("document.getElementById('tau2').value = '0'; compute();")
        time.sleep(0.3)
        pi_narrow = self._js("return window._lastResult.piNNT;")

        # tau² = 0.01 (small enough that PI stays beneficial)
        self._js("document.getElementById('tau2').value = '0.01'; compute();")
        time.sleep(0.3)
        pi_wide = self._js("return window._lastResult.piNNT;")

        self.assertIsNotNone(pi_narrow, 'PI should be estimable for k=10')
        self.assertIsNotNone(pi_wide, 'PI should be estimable for k=10')

        width_narrow = pi_narrow[1] - pi_narrow[0]
        width_wide = pi_wide[1] - pi_wide[0]
        self.assertGreater(width_wide, width_narrow,
            f'PI width with tau²=0.01 ({width_wide:.1f}) should exceed tau²=0 ({width_narrow:.1f})')

    # ── 29: Cost per event scales with cost input ────────────────

    def test_29_cost_scales(self):
        self._js("""
            document.getElementById('exampleSelect').value = 'sglt2i';
            document.getElementById('exampleSelect').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.3)
        cost1 = self._js("return window._lastResult.costPerEventPrevented;")

        self._js("document.getElementById('costPerTx').value = '20000'; compute();")
        time.sleep(0.2)
        cost2 = self._js("return window._lastResult.costPerEventPrevented;")

        self.assertGreater(cost2, cost1, 'Doubling treatment cost should increase cost per event')

    # ── 30: About modal focus trap ───────────────────────────────

    def test_30_about_modal_focus_trap(self):
        """About modal should have aria-modal=true and focus trap."""
        modal = self.driver.find_element(By.ID, 'aboutModal')
        self.assertEqual(modal.get_attribute('aria-modal'), 'true')
        self.assertEqual(modal.get_attribute('role'), 'dialog')


if __name__ == '__main__':
    unittest.main(verbosity=2)
