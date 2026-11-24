from pii_guard import mask, unmask, valid_cnj, valid_cnpj, valid_cpf


def cnj(n="0001234", aaaa="2024", j="8", tr="24", o="0001"):
    dd = 98 - (int(n + aaaa + j + tr + o + "00") % 97)
    return f"{n}-{dd:02d}.{aaaa}.{j}.{tr}.{o}"


def test_cpf_validation():
    assert valid_cpf("529.982.247-25")
    assert not valid_cpf("529.982.247-26")
    assert not valid_cpf("111.111.111-11")


def test_cnpj_validation():
    assert valid_cnpj("11.222.333/0001-81")
    assert not valid_cnpj("11.222.333/0001-82")


def test_cnj_validation():
    assert valid_cnj(cnj())
    assert not valid_cnj(cnj().replace("-", "-0")[:25])


def test_masks_all_kinds():
    text = (f"Cliente 529.982.247-25, CNPJ 11.222.333/0001-81, processo {cnj()}, "
            "fone (48) 99999-1234, mail ana@example.com, CEP 88010-400.")
    m = mask(text)
    for kind in ("CPF", "CNPJ", "CNJ", "PHONE", "EMAIL", "CEP"):
        assert f"[{kind}_1]" in m.text, kind
    assert "529.982" not in m.text and "example.com" not in m.text


def test_invalid_numbers_are_left_alone():
    assert mask("pedido 123.456.789-00").text == "pedido 123.456.789-00"


def test_same_value_same_token_and_roundtrip():
    t = "A 529.982.247-25 e de novo 52998224725."
    m = mask(t)
    assert m.text == "A [CPF_1] e de novo [CPF_1]."
    assert unmask(m.text, m.mapping) == "A 529.982.247-25 e de novo 529.982.247-25."


def test_cnj_not_eaten_by_phone():
    assert mask(cnj()).text == "[CNJ_1]"


def test_kinds_filter():
    m = mask("ana@example.com 88010-400", kinds={"EMAIL"})
    assert m.text == "[EMAIL_1] 88010-400"
