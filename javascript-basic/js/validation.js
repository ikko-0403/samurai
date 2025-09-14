// チェックボタンのクリック時にバリデーションを行う
const button = document.getElementById('check-btn');
button.addEventListener('click', validation);

// バリデーションを行う関数
function validation() {
    // フォームにおける各要素の値を取得
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const output = document.getElementById('output');

    // エラーメッセージを格納する配列（最初は空）
    let errors = [];

    // お名前のバリデーション
    if (name.trim() === '') {
        errors.push('お名前を入力してください。');
    } else if (name.length > 10) {
        errors.push('お名前が10文字を超えています。');
    }

    // メールアドレスのバリデーション（使える記号は.と@のみとする）
    const emailPattern = /^[a-zA-Z0-9.]+@[a-zA-Z0-9.]+$/;
    if (!emailPattern.test(email)) {
        errors.push('メールアドレスの入力形式が正しくありません。');
    }

    // エラーがあれば画面に表示
    if (errors.length > 0) {
        // 配列を改行区切りの文字列に変換して画面に表示
        output.innerHTML = errors.join('<br>');
    } else {
        output.innerHTML = ''; // エラーメッセージをクリア
        alert('バリデーションOKです。');
    }
}