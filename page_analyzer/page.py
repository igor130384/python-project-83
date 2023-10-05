from bs4 import BeautifulSoup


def get_content_of_page(page_data):
    soup = BeautifulSoup(page_data.text, 'html.parser')
    if soup.h1:
        h1 = soup.h1.get_text()
    else:
        h1 = ''
    if soup.title:
        title = soup.title.get_text()
    else:
        title = ''
    atrmeta = soup.find_all("meta", attrs={"name": "description",
                                           "content": True})
    if atrmeta == []:
        meta = ''
    else:
        soup1 = BeautifulSoup(str(atrmeta[0]), 'html.parser')
        meta = soup1.meta['content']
    return h1, title, meta