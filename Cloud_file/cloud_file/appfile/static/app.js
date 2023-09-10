function createCloud() {
    window.location.href = "create/";
}

function goMain() {
    window.location.href = "{% url 'index'%}";
}

window.addEventListener('DOMContentLoaded', () => {
  const uploadForm = document.getElementById('upload-form');
  const loadingPage = document.getElementById('loading-page');

  uploadForm.addEventListener('submit', () => {

    loadingPage.style.display = 'block';
  });
});