// script.js FINAL avec affichage du temps de blocage sur l'interface
let qrScanner;
let decryptButton;

// Évaluation en temps réel
document.addEventListener("DOMContentLoaded", () => {
  const keyInput = document.getElementById("key");
  decryptButton = document.querySelector("button.secondary");
  if (keyInput) {
    keyInput.addEventListener("input", function (e) {
      evaluateKeyStrength(e.target.value);
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
    display.textContent = "🔴 Clé faible";
    display.style.color = "red";
  } else if (score <= 4) {
    display.textContent = "🟡 Clé moyenne";
    display.style.color = "orange";
  } else {
    display.textContent = "🟢 Clé forte";
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
  qrDisplay.innerHTML = `<img src="${qrURL}" alt="QR Code"><br><a href="${qrURL}" download="QRCode.png">📥 Télécharger QR</a>`;
}

function startScanner() {
  const keyInput = document.getElementById('key');
  const reader = document.getElementById('reader');
  const status = document.getElementById('status');

  Html5Qrcode.getCameras().then(cameras => {
    if (cameras.length === 0) {
      status.textContent = "❌ Aucune caméra trouvée.";
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
        status.textContent = "✅ Clé détectée via QR.";
        qrScanner.stop().then(() => reader.innerHTML = "");
      }
    );
  });
}

function stopScanner() {
  const reader = document.getElementById('reader');
  if (qrScanner) {
    qrScanner.stop().then(() => {
      reader.innerHTML = "";
    });
  }
}

function analyseIAEtChiffrer() {
  const file = document.getElementById('file').files[0];
  const key = document.getElementById('key').value;
  const status = document.getElementById('status');

  if (!file || !key) {
    status.textContent = "❗ Veuillez sélectionner un fichier et entrer une clé.";
    return;
  }

  evaluateKeyStrength(key);

  const formData = new FormData();
  formData.append("file", file);

  status.innerHTML = "🧠 <span style='color:#007BFF;'>Analyse IA en cours...</span>";

  fetch("http://localhost:5000/analyse_ai", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.sensibles) {
        status.innerHTML = `⚠️ <span style='color:#b80000;'>Fichier sensible détecté :</span><br><strong style='color:#a00;'>${data.message.replaceAll('\n', '<br>')}</strong>`;
        showModal(data.message, () => {
          handleEncrypt();
        });
      } else {
        status.innerHTML = "✅ <span style='color:green;'>Aucune donnée sensible détectée.</span>";
        handleEncrypt();
      }
    })
    .catch(err => {
      status.innerHTML = "❌ Erreur IA : " + err.message;
    });
}

function handleEncrypt() {
  const file = document.getElementById('file').files[0];
  const key = document.getElementById('key').value;
  const status = document.getElementById('status');

  const formData = new FormData();
  formData.append("file", file);
  formData.append("key", key);

  status.innerHTML += "<br>🔐 <span style='color:#007BFF;'>Chiffrement en cours...</span>";

  fetch("http://localhost:5000/encrypt", {
    method: "POST",
    body: formData
  })
    .then(res => {
      if (!res.ok) throw new Error("Erreur serveur");
      return res.blob();
    })
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = file.name + ".enc";
      a.click();
      status.innerHTML += "<br>✅ Fichier chiffré avec succès.";
    })
    .catch(err => {
      status.innerHTML += "<br>❌ Erreur : " + err.message;
    });
}

function handleDecrypt() {
  const file = document.getElementById('file').files[0];
  const key = document.getElementById('key').value;
  const status = document.getElementById('status');

  if (decryptButton && decryptButton.disabled) {
    status.innerHTML = "⏳ Vous êtes encore bloqué. Veuillez patienter...";
    return;
  }

  if (!file || !key) {
    status.textContent = "❗ Fichier ou clé manquant.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("key", key);

  status.textContent = "🔓 Déchiffrement en cours...";

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
      a.download = "fichier_dechiffre";
      a.click();
      status.textContent = "✅ Déchiffrement réussi.";
    })
    .catch(err => {
      status.innerHTML = "❌ " + err.message;
      if (err.message.includes("⏱ Accès temporairement bloqué")) {
        const match = err.message.match(/\((\d+) sec\)/);
        if (match && match[1]) {
          const seconds = parseInt(match[1]);
          bloquerBoutonDecrypt(seconds);
        }
      }
    });
}

function bloquerBoutonDecrypt(secRestant) {
  const status = document.getElementById('status');
  if (!decryptButton) return;
  decryptButton.disabled = true;
  let compteur = secRestant;

  const interval = setInterval(() => {
    status.innerHTML = `⏱ Déchiffrement bloqué : <strong>${compteur} secondes restantes</strong>`;
    compteur--;
    if (compteur <= 0) {
      clearInterval(interval);
      decryptButton.disabled = false;
      status.innerHTML = "🔓 Vous pouvez réessayer le déchiffrement.";
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
    document.getElementById('status').innerHTML += "<br>⛔ <span style='color:orange;'>Chiffrement annulé par l'utilisateur.</span>";
  };
}
