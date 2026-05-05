// Substitua pelo IP que o seu ESP32 pegar no WiFi do celular
var esp32IP = "http://192.168.43.100";

function mudarIP() {
  esp32IP = "http://" + document.getElementById('ipInput').value;
}

async function dispararAcao(rota) {
    try {
        const resposta = await fetch(`${esp32IP}${rota}`);
        
        if (resposta.ok) {
            console.log(`Sucesso: A rota ${rota} foi ativada!`);
        } else {
            console.error(`O ESP32 retornou um erro na rota ${rota}`);
        }
    } catch (erro) {
        console.error(`Erro de rede ao tentar acessar ${rota}:`, erro);
    }
}

function lancarCarrinho() {
    dispararAcao('/lancar');
}

function buzinar() {
    dispararAcao('/buzinar');
}

async function mudarFrequencia(novaFrequencia) {
    try {
        // Enviando o dado via "Query String" (Ex: /mudarFrequencia?valor=100)
        const resposta = await fetch(`${esp32IP}/mudarFrequencia?valor=${novaFrequencia}`);
        
        if (resposta.ok) {
            console.log(`Frequência alterada para: ${novaFrequencia}`);
        }
    } catch (erro) {
        console.error('Erro ao mudar a frequência:', erro);
    }
}

async function buscarHistorico() {
    try {
        const resposta = await fetch(`${esp32IP}/historico`);
        
        if (resposta.ok) {
            const dados = await resposta.json();
            
            console.log("Histórico recebido:", dados);
            
            // Exemplo imaginando que o ESP32 retorna: { voltas: [25.4, 26.1, 24.8] }
            atualizarTelaComHistorico(dados);
        }
    } catch (erro) {
        console.error('Erro ao buscar o histórico:', erro);
    }
}

// Função auxiliar para jogar o histórico no HTML
function atualizarTelaComHistorico(dados) {
    // Imagine que você tem uma div com id="lista-historico" no seu HTML
    // const lista = document.getElementById('lista-historico');
    // lista.innerHTML = ''; 
    // dados.voltas.forEach(volta => {
    //     lista.innerHTML += `<li>Velocidade: ${volta} km/h</li>`;
    // });
}
