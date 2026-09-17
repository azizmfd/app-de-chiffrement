let qrScanner;
let decryptButton;

// Real-time key strength evaluation and AOS initialization
document.addEventListener("DOMContentLoaded", () => {
  const keyInput = document.getElementById("key");
  decryptButton = document.querySelector("button.btn-danger");
  if (keyInput) {
    keyInput.addEventListener("input", function (e) {
      evaluateKeyStrength(e.target.value);
    });
  }
  if (typeof AOS !== 'undefined') {
    AOS.init({ duration: 800, once: true });
  }

  // Gestion affichage nom fichier choisi (custom file input)
  const fileInput = document.getElementById("file");
  const fileNameSpan = document.getElementById("fileName");

  if (fileInput && fileNameSpan) {
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length > 0) {
        fileNameSpan.textContent = fileInput.files[0].name;
      } else {
        fileNameSpan.textContent = "";
      }
    });
  }
});

function evaluateKeyStrength(key) {
  const display = document.getElementById("keyStrength");
  if (!display) return;

  const length = key.length;
  const hasNumbers = /\d/.test(key);
  const hasSymbols = /[!@#$%^&*()_\-+=<>?/{}~]/.test(key);
  const hasUpper = /[A-Z]/.test(key);
  const hasLower = /[a-z]/.test(key);

  let score = 0;
  if (length >= 8) score++;
  if (length >= 12) score++;
  if (hasNumbers) score++;
  if (hasSymbols) score++;
  if (hasUpper && hasLower) score++;

  if (score <= 2) {
    display.textContent = "🔴 Weak key";
    display.style.color = "red";
  } else if (score <= 4) {
    display.textContent = "🟡 Medium key";
    display.style.color = "orange";
  } else {
    display.textContent = "🟢 Strong key";
    display.style.color = "green";
  }
}

function generateStrongKey() {
  const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#%*-_$";
  let key = "";
  for (let i = 0; i < 24; i++) {
    key += charset[Math.floor(Math.random() * charset.length)];
  }
  document.getElementById('key').value = key;
  evaluateKeyStrength(key);
}

function generateQRCodeFromKey() {
  const key = document.getElementById('key').value;
  const qrDisplay = document.getElementById('qrDisplay');
  if (!key) return;
  const qrURL = `https://api.qrserver.com/v1/create-qr-code/?data=${encodeURIComponent(key)}&size=150x150`;
  qrDisplay.innerHTML = `<img src="${qrURL}" alt="QR Code"><br><a href="${qrURL}" download="QRCode.png">📥 Download QR</a>`;
}

function startScanner() {
  const keyInput = document.getElementById('key');
  const reader = document.getElementById('reader');
  const status = document.getElementById('status');

  Html5Qrcode.getCameras().then(cameras => {
    if (cameras.length === 0) {
      status.textContent = "❌ No camera found.";
      return;
    }

    qrScanner = new Html5Qrcode("reader");
    qrScanner.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: 250 },
      decodedText => {
        keyInput.value = decodedText;
        evaluateKeyStrength(decodedText);
        generateQRCodeFromKey();
        status.textContent = "✅ Key detected via QR.";
        qrScanner.stop().then(() => reader.innerHTML = "");
      }
    );
  }).catch(err => {
    status.textContent = "❌ Camera error: " + err;
  });
}

function stopScanner() {
  const reader = document.getElementById('reader');
  if (qrScanner) {
    qrScanner.stop().then(() => {
      reader.innerHTML = "";
    }).catch(err => {
      console.error("Error stopping scanner:", err);
    });
  }
}

function analyseIAEtChiffrer() {
  const file = document.getElementById('file').files[0];
  const key = document.getElementById('key').value;
  const status = document.getElementById('status');

  if (!file || !key) {
    status.textContent = "❗ Please select a file and enter a key.";
    return;
  }

  evaluateKeyStrength(key);

  const formData = new FormData();
  formData.append("file", file);

  status.innerHTML = "🧠 <span style='color:#007BFF;'>AI analysis in progress...</span>";

  fetch("http://localhost:5000/analyse_ai", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.sensibles) {
        status.innerHTML = `⚠️ <span style='color:#b80000;'>Sensitive file detected:</span><br><strong style='color:#a00;'>${data.message.replaceAll('\n', '<br>')}</strong>`;
        showModal(data.message, () => {
          handleEncrypt();
        });
      } else {
        status.innerHTML = "✅ <span style='color:green;'>No sensitive data detected.</span>";
        handleEncrypt();
      }
    })
    .catch(err => {
      status.innerHTML = "❌ AI error: " + err.message;
    });
}

function handleEncrypt() {
  const file = document.getElementById('file').files[0];
  const key = document.getElementById('key').value;
  const status = document.getElementById('status');

  const formData = new FormData();
  formData.append("file", file);
  formData.append("key", key);

  status.innerHTML = "🔐 <span style='color:#007BFF;'>Encryption in progress...</span>";

  fetch("http://localhost:5000/encrypt", {
    method: "POST",
    body: formData
  })
    .then(res => {
      if (!res.ok) throw new Error("Server error");
      return res.blob();
    })
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = file.name + ".enc";
      a.click();

      status.innerHTML = "✅ File encrypted successfully.";

      // Optionally clear message after 3 seconds
      // setTimeout(() => { status.innerHTML = ""; }, 3000);
    })
    .catch(err => {
      status.innerHTML = "❌ Error: " + err.message;
    });
}

function handleDecrypt() {
  const file = document.getElementById('file').files[0];
  const key = document.getElementById('key').value;
  const status = document.getElementById('status');

  if (decryptButton && decryptButton.disabled) {
    status.innerHTML = "⏳ Please wait before trying to decrypt again...";
    return;
  }

  if (!file || !key) {
    status.textContent = "❗ File or key missing.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("key", key);

  status.textContent = "🔓 Decryption in progress...";

  fetch("http://localhost:5000/decrypt", {
    method: "POST",
    body: formData
  })
    .then(res => {
      if (!res.ok) return res.json().then(data => { throw new Error(data.error); });
      return res.blob();
    })
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "decrypted_file";
      a.click();

      status.textContent = "✅ Decryption successful.";
    })
    .catch(err => {
      status.innerHTML = "❌ " + err.message;
      if (err.message.includes("⏱ Temporary access blocked")) {
        const match = err.message.match(/\((\d+) sec\)/);
        if (match && match[1]) {
          const seconds = parseInt(match[1]);
          blockDecryptButton(seconds);
        }
      }
    });
}

function blockDecryptButton(secondsRemaining) {
  const status = document.getElementById('status');
  if (!decryptButton) return;
  decryptButton.disabled = true;
  let counter = secondsRemaining;

  const interval = setInterval(() => {
    status.innerHTML = `⏱ Decryption blocked: <strong>${counter} seconds remaining</strong>`;
    counter--;
    if (counter <= 0) {
      clearInterval(interval);
      decryptButton.disabled = false;
      status.innerHTML = "🔓 You can try decryption again.";
    }
  }, 1000);
}

function showModal(message, onConfirm) {
  const modal = document.getElementById("confirmModal");
  const modalMessage = document.getElementById("modalMessage");
  modalMessage.innerHTML = message.replaceAll('\n', '<br>');
  modal.style.display = "block";

  document.getElementById("confirmYes").onclick = function () {
    modal.style.display = "none";
    onConfirm();
  };

  document.getElementById("confirmNo").onclick = function () {
    modal.style.display = "none";
    document.getElementById('status').innerHTML += "<br>⛔ <span style='color:orange;'>Encryption canceled by user.</span>";
  };
}
