const pushBtn = document.getElementById('btn');
const textChange = document.getElementById("text");

pushBtn.addEventListener('click', () => {
  textChange.textContent = 'ボタンをクリックしました'
});