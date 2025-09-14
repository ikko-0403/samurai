const pushBtn = document.getElementById('btn');
const textChange = document.getElementById("text");

pushBtn.addEventListener('click', () => {
    setTimeout(() => {
      textChange.textContent = 'ボタンをクリックしました'
    }, 2000)
});