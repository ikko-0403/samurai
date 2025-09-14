// クッキーを取得する関数
const getCookie = (name) => {
    // 「;」で区切り、個々のクッキーを配列で取得
    const cookies = document.cookie.split(';');

    // クッキーをfor文で1つずつチェック
    for (let i = 0; i < cookies.length; i++) {
        // 「=」でクッキーを分割し、クッキー名と値を取得
        const [cookieName, value] = cookies[i].trim().split('=');

        // クッキー名が一致したら、その値をデコードしてreturn
        if (cookieName === name) {
            return decodeURIComponent(value);
        }
    }
    // 見つからなかったら空文字をreturn
    return '';
}

// クッキーを取得して画面に表示
document.getElementById('output').textContent = 'name=' + getCookie('name') + 'age=' + getCookie('age');

// クッキーを作成
document.cookie = 'name=' + encodeURIComponent('侍太郎') + '; max-age=' + 60 * 60;
document.cookie = 'age=30; max-age=' + 60 * 60;