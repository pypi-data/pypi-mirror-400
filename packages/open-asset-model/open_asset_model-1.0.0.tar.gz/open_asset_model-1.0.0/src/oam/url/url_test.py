import json
from oam.url.url import URL
from oam.asset import Asset
from oam.asset import AssetType

def test_url_key():
    want = "https://owasp.org/"
    url = URL(want)
    assert url.key == want
        
def test_url_asset_type():
    url = URL("https://owasp.org/")
    assert url.asset_type == AssetType.URL

def test_url_implements_asset():
    assert issubclass(URL, Asset)
    
def test_url_json():
    url = URL(
	raw="http://user:pass@example.com:8080/path?option1=value1&option2=value2#fragment",
        scheme="http",
        username="user",
	password="pass",
	host="example.com",
	port=8080,
	path="/path",
	options="option1=value1&option2=value2",
	fragment="fragment",
    )

    expectedJSON = {
        "url":"http://user:pass@example.com:8080/path?option1=value1&option2=value2#fragment",
        "scheme":"http",
        "host":"example.com",
        "path":"/path",
        "username":"user",
        "password":"pass",
        "port":8080,
        "options":"option1=value1&option2=value2",
        "fragment":"fragment"
    }
    
    assert json.dumps(expectedJSON) == url.to_json()
    
def test_url_from_text():
    url = URL.from_text("http://user:pass@example.com:8080/path?option1=value1&option2=value2#fragment")

    want = URL(
        raw="http://user:pass@example.com:8080/path?option1=value1&option2=value2#fragment",
        scheme="http",
        host="example.com",
        path="/path",
        username="user",
        password="pass",
        port=8080,
        options="option1=value1&option2=value2",
        fragment="fragment"
    )
    
    assert url.raw == want.raw
    assert url.scheme == want.scheme
    assert url.host == want.host
    assert url.path == want.path
    assert url.username == want.username
    assert url.password == want.password
    assert url.port == want.port
    assert url.options == want.options
    assert url.fragment == want.fragment
