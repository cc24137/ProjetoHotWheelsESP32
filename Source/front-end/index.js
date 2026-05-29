// Aqui você pode colocar o IP local ou o link do Ngrok (ex: https://a1b2-c3d4.ngrok-free.app)
var baseUrl = "http://192.168.43.100";

function mudarIP() {
    let inputUrl = document.getElementById('ipInput').value;

    // Limpa a barra final se o usuário digitar sem querer
    if (inputUrl.endsWith('/')) {
        inputUrl = inputUrl.slice(0, -1);
    }

    // Se o usuário digitou apenas o IP (ex: 192.168.1.10), adiciona o http://
    // Se ele colou o link inteiro do ngrok (https://...), mantém como está
    if (!inputUrl.startsWith('http')) {
        baseUrl = "http://" + inputUrl;
    } else {
        baseUrl = inputUrl;
    }

    console.log("Conectando em:", baseUrl);
}

// ------------------------------------------------
// 1. ROTAS POST SIMPLES (Lançar e Buzinar)
// ------------------------------------------------
async function dispararAcao(rota) {
    try {
        const resposta = await fetch(`${baseUrl}${rota}`, {
            method: 'POST', // <- Ajustado para bater com o Python
            headers: {
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true' // <- Pula a tela de aviso do Ngrok
            },
            body: JSON.stringify({}) // O Microdot espera um JSON, mesmo que vazio
        });

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

// ------------------------------------------------
// 2. ROTA POST COM DADOS (Mudar Frequência)
// ------------------------------------------------
async function mudarFrequencia(novaFrequencia) {
    try {
        // Seu Python faz: nova_freq = int(data.get("frequencia"))
        // Então mandamos o dado dentro do "body" em vez da URL
        const resposta = await fetch(`${baseUrl}/mudarFrequencia`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            },
            body: JSON.stringify({ "frequencia": novaFrequencia })
        });

        if (resposta.ok) {
            console.log(`Frequência alterada para: ${novaFrequencia}`);
        }
    } catch (erro) {
        console.error('Erro ao mudar a frequência:', erro);
    }
}

// ------------------------------------------------
// 3. ROTA GET (Buscar Histórico)
// ------------------------------------------------
async function buscarHistorico() {
    try {
        const resposta = await fetch(`${baseUrl}/historico`, {
            method: 'GET', // Essa rota é GET no seu Python
            headers: {
                'ngrok-skip-browser-warning': 'true' // Necessário até no GET por causa do Ngrok
            }
        });

        if (resposta.ok) {
            const dados = await resposta.json();
            console.log("Histórico recebido:", dados);
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
    // dados.forEach(lancamento => {
    //     lista.innerHTML += `<li>${lancamento}</li>`;
    // });
}
