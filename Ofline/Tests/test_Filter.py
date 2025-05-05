import check_swear
import pytest
from Ofline.config import russ_mat,eng_mat,extr
from Ofline.BadWordFilter import FilterBadWords,white_list
import asyncio




filter=FilterBadWords()

@pytest.mark.parametrize("word_not_bad,expected",[(word,False) for word in white_list])
def test_group1_filter(word_not_bad,expected):
    res=asyncio.run(filter.check_bad_words(word_not_bad,filter.bad_words_patterns))
    assert res==False


@pytest.mark.parametrize("word_bad,expected",[(word,True) for word in russ_mat])
def test_group2_filter(word_bad,expected):
    res=asyncio.run(filter.check_bad_words(word_bad,filter.bad_words_patterns))
    assert res==expected

@pytest.mark.parametrize("word_symbols,expected",[
    ("бл*",True),
("бл9",True),
("бляяяяяяя",True),
("бл",True),
("бл999999ять",True),
("сук@",True),
("ебл@н",True),
("сyкa",True), #тут вместо русских гласных букв английские
("п1здец",True),
("п!зд@",True),
("Eбл@@@@",True),
("6ля",True),
("6лядин@",True),
("dolbaeb",True),
("pizda",True),
("пizda",True),
("$уka",True),
])
def test_group3_filter(word_symbols,expected):
    res = asyncio.run(filter.check_bad_words(word_symbols, filter.bad_words_patterns))
    assert res == expected


@pytest.mark.parametrize("word_bad,expected",[(word,True) for word in extr])
def test_group4_filter(word_bad,expected):
    res=asyncio.run(filter.check_bad_words(word_bad,filter.bad_words_patterns))
    assert res==expected

