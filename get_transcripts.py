from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

def scrape_episode(ep_num):
    """
    Scrape an episode transcript from avatarspirit.net and parse it into a plaintext format,
    which only contains dialogue. Each line is of the form [Character: spoken dialogue]. 
    """
    url = f'http://atla.avatarspirit.net/transcripts.php?num={ep_num}'
    html = urlopen(url)
    soup = BeautifulSoup(html.read(), features='lxml')
    script_text = ' '.join([
        t for line in soup.find('blockquote').children \
        if (t:=(str(line).strip().replace('\r', '').replace('</b>', ':') \
        if line.name=='b' or not hasattr(line, 'get_text') else line.get_text()))
    ])
    script_lines = script_text.split('<b>')
    return clean_transcript(script_lines)

def clean_transcript(script_lines):
    """Strip out everything but dialogue and character names."""
    # Remove everything before Act I begins
    try:
        act_i_idx = next(i for i in range(len(script_lines)) if 'Act I' in script_lines[i])
        script_lines = script_lines[act_i_idx+1:]
    except StopIteration:
        # The Tales of Ba Sing Se
        start_idx = next(i for i in range(len(script_lines)) if 'The Tale of' in script_lines[i])
        script_lines = [line for line in script_lines[start_idx:] if 'The Tale of' not in line]

    script_lines = [
        re.sub('([\(\[]).*?([\)\]])', '',           # Remove all text in parens/brackets
        re.sub('Act (I+|I*VI*|I*XI*)', '', l))      # Remove "Act _"
        .strip() for line in script_lines
        if '::' in (l := line.replace(': :', '::')) # Remove any stray lines without dialogue
                                                    # (negligible cases of two people speaking at once)
    ]
    return (f'{l.strip()}\n' for l in script_lines)

# Scrape all episodes and write each to a file
for season in range(1, 4):
    for episode in range(1, 21):
        ep_num = f'{season}{str(episode).zfill(2)}'
        script_lines = list(scrape_episode(ep_num))
        with open(f'transcripts/{ep_num}.txt', mode='w') as f:
            f.writelines(script_lines)
        assert sum(l.count('::') for l in script_lines) == len(list(script_lines))