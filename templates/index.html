<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIGNAL MEXICAIN</title>
    <style>
        body { background: #0e1015; color: #fff; font-family: sans-serif; text-align: center; padding: 20px; }
        .box { background:#1c1f26; padding:20px; border-radius:15px; margin:20px; border:1px solid #333; }
        .btn { padding: 15px 40px; border-radius: 30px; border:none; font-weight:bold; cursor:pointer; width:80%; margin-top:10px; }
    </style>
</head>
<body>

<div id="app-container">
    <h2>Vérification VIP...</h2>
</div>

<script>
    // 1. Vérification automatique au démarrage
    async function verifierVIP() {
        const player_id = "ID_UTILISATEUR"; // Dans Telegram, récupère l'ID réel via WebApp
        const response = await fetch('/verifier-vip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ player_id: player_id })
        });

        if (response.status === 200) {
            afficherInterface();
        } else {
            document.getElementById('app-container').innerHTML = "<h2>❌ Accès refusé</h2><p>Veuillez contacter l'admin pour valider votre compte.</p>";
        }
    }

    function afficherInterface() {
        document.getElementById('app-container').innerHTML = `
            <div id="interface">
                <h2 id="titre">Signal</h2>
                <div id="res" class="box" style="display:none;">
                    <p>Cote cible</p>
                    <div id="cote" style="font-size:32px; color:#00ffcc; font-weight:bold;">--</div>
                    <p>Début du signal: <span id="heure">--</span></p>
                    <p>Fiabilité: <span id="fiab">--</span></p>
                </div>
                <button class="btn" style="background:#00ffcc" onclick="calc()">DEMANDER SIGNAL</button>
            </div>
        `;
    }

    // Logique de cycle (30s pour Lucky, 50s pour les autres)
    function calc() {
        const jeu = "Lucky Jet"; // À adapter dynamiquement selon le jeu cliqué
        const sFixe = (jeu === 'Lucky Jet') ? 30 : 50;
        const cycleEnSecondes = 4 * 60; // 4 minutes
        
        const now = Math.floor(Date.now() / 1000);
        const prochainTs = Math.ceil(now / cycleEnSecondes) * cycleEnSecondes;
        const d = new Date(prochainTs * 1000);
        d.setUTCSeconds(sFixe);

        document.getElementById('res').style.display = 'block';
        document.getElementById('cote').innerText = (Math.random() * (15 - 2) + 2).toFixed(2) + "x";
        document.getElementById('heure').innerText = d.getUTCHours().toString().padStart(2,'0') + ":" + d.getUTCMinutes().toString().padStart(2,'0') + ":" + sFixe + " UTC";
        document.getElementById('fiab').innerText = "2.0";
    }

    verifierVIP();
</script>
</body>
</html>
