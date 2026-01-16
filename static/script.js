/*
 * @Description: 
 * @Author: QiLan Gao
 * @Date: 2025-06-06 12:16:22
 * @LastEditTime: 2025-06-06 12:48:59
 * @LastEditors: QiLan Gao
 */

function uploadImage(blobOrFile = null) {
    const fileInput = document.getElementById("file-input");
    const resultText = document.getElementById("result-text");
    const formData = new FormData();

    let file = blobOrFile || fileInput.files[0];
    if (!file) {
        alert("请先选择或粘贴一张图片");
        return;
    }

    formData.append("file", file);

    fetch("/recognize", {
        method: "POST",
        body: formData,
    })
    .then(resp => resp.json())
    .then(data => {
        if (data.error) {
            resultText.innerText = "识别出错：" + data.error;
        } else {
            const imgUrl = location.origin + "/uploads/" + data.image;
            document.getElementById("image-preview").innerHTML = `<img src="${imgUrl}" style="max-width: 100%; max-height: 100%;">`;
            resultText.innerText = data.result;
        }
    })
    .catch(err => {
        resultText.innerText = "请求失败：" + err;
    });
}

// 监听文件选择立即上传
document.getElementById("file-input").addEventListener("change", function () {
    if (this.files[0]) {
        uploadImage(this.files[0]);
    }
});

// 监听 Ctrl+V 粘贴图片
window.addEventListener('paste', function (event) {
    const items = event.clipboardData && event.clipboardData.items;
    if (!items) return;

    for (const item of items) {
        if (item.type.indexOf("image") === 0) {
            const file = item.getAsFile();
            uploadImage(file);
            break;
        }
    }
});
