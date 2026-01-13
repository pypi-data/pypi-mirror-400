import re
from html import unescape

class HtmlScrap:

    def __init__(self):
        # Compile regex patterns sekali saja
        self.captcha_pattern = re.compile(
            r'class=["\']([^"\']+)["\'][^>]*data-sitekey=["\']([^"\']+)["\'][^>]*>',
            re.IGNORECASE
        )
        self.input_pattern = re.compile(
            r'<input[^>]*name=["\'](.*?)["\'][^>]*value=["\'](.*?)["\'][^>]*>',
            re.IGNORECASE
        )
        self.limit_pattern = re.compile(
            r'(\d{1,})\/(\d{1,})',
            re.IGNORECASE
        )
        self.option_pattern = re.compile(
            r'<option\s+value=["\']([^"\']+)["\'][^>]*>',
            re.IGNORECASE
        )

    def _scrap(self, pattern, html):
        """Gunakan compiled pattern"""
        return pattern.findall(html)

    def _get_captcha(self, html):
        data = {}
        scrap = self._scrap(self.captcha_pattern, html)
        for cls, sitekey in scrap:
            data[cls] = sitekey
        return data

    def _get_option_values(self, html):
        return [val for (val,) in self._scrap(self.option_pattern, html)]

    def _get_input(self, html, form_index=1):
        data = {}
        forms = html.split('<form')
        if len(forms) <= form_index:
            return data
        form_content = forms[form_index]
        scrap = self._scrap(self.input_pattern, form_content)
        for name, value in scrap:
            data[name] = value
        return data

    def result(self, html, form_index=1):
        data = {}

        # title
        title = ''
        if '<title>' in html:
            parts = html.split('<title>')
            if len(parts) > 1:
                title = parts[1].split('</title>')[0]
        data['title'] = title

        # cloudflare / firewall / locked
        data['cloudflare'] = 'Just a moment...' in html
        data['firewall']   = 'Firewall' in html
        data['locked']     = 'Locked' in html
        data['captcha']    = self._get_captcha(html)
        data['options']    = self._get_option_values(html)

        # input
        input_data = self._get_input(html, form_index)
        data['input'] = input_data if input_data else self._get_input(html, 2)

        # faucet limit
        data['faucet'] = self._scrap(self.limit_pattern, html)

        # response defaults
        data['response'] = {
            'success': False,
            'warning': None,
            'unset': False,
            'exit': False
        }

        # success message
        if "icon: 'success'," in html:
            try:
                success_html = html.split("icon: 'success',")[1].split("html: '")[1].split("'")[0]
                data['response']['success'] = unescape(success_html)
            except IndexError:
                pass
        else:
            warning = None
            if "html: '" in html:
                try:
                    warning = html.split("html: '")[1].split("'")[0]
                except IndexError:
                    warning = None
            # set default
            data['response']['warning'] = "Not Found"
            data['response']['exit'] = False
            data['response']['unset'] = False

            if 'Your account' in html:
                try:
                    ban = html.split('<div class="alert text-center alert-danger"><i class="fas fa-exclamation-circle"></i> Your account')[1].split('</div>')[0]
                    data['response']['warning'] = ban
                    data['response']['exit'] = True
                except IndexError:
                    pass
            elif 'invalid amount' in html:
                data['response']['warning'] = "You are sending an invalid amount"
                data['response']['unset'] = True
            elif 'Invalid API Key used' in html:
                data['response']['warning'] = "Invalid API Key used"
                data['response']['unset'] = True
            elif ('Shortlink in order to claim from the faucet!' in html or
                  'Shortlink must be completed' in html):
                data['response']['warning'] = warning or "Shortlink required"
                data['response']['exit'] = True
            elif 'sufficient funds' in html:
                data['response']['warning'] = "Sufficient funds"
                data['response']['unset'] = True
            elif 'Daily claim limit' in html:
                data['response']['warning'] = "Daily claim limit"
                data['response']['unset'] = True
            elif warning:
                data['response']['warning'] = warning

        return data
