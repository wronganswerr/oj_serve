import requests
from bs4 import BeautifulSoup


url = 'https://codeforces.com/problemset/problem/2036/A'
response = requests.get(url)

if response.status_code != 200:
    print(response)
else:
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取标题
    title = soup.find('div', class_='title').text.strip()

    # 获取题面
    problem_text = soup.find('div', class_='problem-statement')

    # 获取样例输入和输出
    input_output_examples = problem_text.find_all('div', class_='input-output-example')

    # 将题面转换为 Markdown
    markdown = f'# {title}\n'
    markdown += problem_text.text.strip() + '\n'

    for example in input_output_examples:
        markdown += '\n' + example.prettify() + '\n'

    # 输出 Markdown
    print(markdown)
