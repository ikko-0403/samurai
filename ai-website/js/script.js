// 画像のリスト
const images = ["images/image1.jpg", "images/image2.jpg", "images/image3.jpg"];

// 現在表示されている画像のインデックス
let currentIndex = 0;

// 画像を切り替える関数
function changeImage() {
    // 次の画像のインデックスを設定
    currentIndex = (currentIndex + 1) % images.length;

    // 画像を変更
    document.getElementById("slide-image").src = images[currentIndex];
}

// 3秒ごとにchangeImage関数を実行
setInterval(changeImage, 3000);