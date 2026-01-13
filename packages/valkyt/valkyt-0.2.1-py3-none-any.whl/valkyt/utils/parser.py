from pyquery import PyQuery
from bs4 import BeautifulSoup

class Parser:
    def __init__(self) -> None:
        pass

    def ex(self, html: PyQuery, selector: str) -> PyQuery:
        result = None
        try:
            html: str = PyQuery(html)
            result = html.find(selector)
        except Exception as err:
            print(err)

        finally:
            return result
        
    
    @staticmethod
    def parser_table(html: PyQuery) -> list:
        soup = BeautifulSoup(html.html(), 'html.parser')

        # Extract table data
        table_data = []
        thead = soup.find('thead')
        tbody = soup.find('tbody')
        tfoot = soup.find('tfoot')

        trHead = thead.select('tr')

        keys = [[] for a in trHead]

        for i, tr in enumerate(trHead):
            for j, th in enumerate(tr.select('th')):
                rowspan = int(th.get('rowspan', 1))
                colspan = int(th.get('colspan', 1))
                text = ' '.join([a.strip() for a in th.text.strip().split('\n')])
                for h in range(colspan):
                    for d in range(i, rowspan):
                        keys[d].append(text)
                    if i > 0:
                        keys[i].append(text)

        keys.reverse()
        result = []
        for tr in tbody.select('tr'):
            res = []
            for j, key in enumerate(keys):
                r = {}
                for i, td in enumerate(tr.select('td')):
                    text = td.text.strip()
                    if j > 0:
                        if key[i] != keys[j - 1][i]:
                            if key[i] not in r: r[key[i]] = {}
                            r[key[i]][keys[j - 1][i]] = res[j - 1][keys[j - 1][i]]
                        else:
                            r[key[i]] = text
                    else:
                        r[key[i]] = text
                    if (a := td.select_one('a')):
                        r['url'] = a.get('href')
                res.append(r)
            result.append(res[-1])
            
        return result