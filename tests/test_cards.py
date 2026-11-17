from zipper9_ui.app import Zipper9App

app = Zipper9App()
app.withdraw()

for key, w in app.algo_cards.items():
    fmt_text = w['fmt'].cget('text')
    algo_text = w['algo'].cget('text')
    sub_text = w['sub'].cget('text')
    print(f"Card [{key}]: fmt='{fmt_text}', algo='{algo_text}', sub='{sub_text}'")
    assert '반디집' not in sub_text, "반디집 단어가 남아있음"

assert app.algo_cards['7z']['sub'].cget('text') == '초고압축'
assert app.algo_cards['7z']['fmt'].cget('text') == '🗜️ 7z'
assert app.algo_cards['7z']['algo'].cget('text') == 'LZMA2'

assert 'ZIP' in app.algo_cards['zstd']['fmt'].cget('text')
assert 'Zstandard' in app.algo_cards['zstd']['algo'].cget('text')

assert 'TAR' in app.algo_cards['lz4']['fmt'].cget('text')
assert 'LZ4' in app.algo_cards['lz4']['algo'].cget('text')

assert 'TAR' in app.algo_cards['targz']['fmt'].cget('text')
assert 'Gzip' in app.algo_cards['targz']['algo'].cget('text')

app.destroy()
print("All Card Layout Tests Passed Successfully!")
