# Relatório do Projeto

## 1. Introdução do Projeto    
O projeto "Hot Wheels" tem como objetivo desenvolver um sistema de monitoramento do percurso de um carrinho de brinquedo ao longo de uma pista com um desfiladeiro no meio. O sistema ficará responsável por detectar a posição do carrinho, calcular sua velocidade e enviar esses dados para uma pagina web em tempo real, sendo possível analisar através de uma conexão wifi com o eps32.

---
## 2. Materiais Utilizados

### Hardware
Para a realização deste projeto, foram utilizados os seguintes componentes de hardware:
- Pista de brinquedo com desfiladeiro
- Lançadeira para o carrinho
- Placa de desenvolvimento ESP32
- Sensores de posição HW-201
- Paínel de led 8*8 max7219
### Software
Para a realização deste projeto foram utilizados os seguintes softwares:
- IDE Thonny para desenvolvimento do código em Python
- Biblioteca MicroPython para ESP32
- Biblioteca para controle do painel de LED MAX7219
- Servidor web para visualização dos dados em tempo real

---

## 3. Desenvolvimento do Projeto
### Metodologia
#### Planejamento
O projeto foi divido nas seguintes etapas:
- Hardware:
    1. Montagem dos sensores e outros equipamentos no simulador Wokwi e testes fisicos
    2. Montagem e testes no esp32
- Software:
    1. Desenvolvimento do código para leitura dos sensores e controle do painel de LED
    2. Desenvolvimento do servidor web para visualização dos dados em tempo real
#### Controle de Versão
Durante o desenvolvimento do projeto, utilizamos o controle de versão para gerenciar as alterações no código e garantir a integridade do projeto. Utilizamos o Git como sistema de controle de versão, permitindo-nos acompanhar as mudanças, colaborar com outros membros da equipe e reverter para versões anteriores, se necessário.

---

## 4. Registros

### 4.1 Fase de Planejamento

![Planejamento](/imagem1.jpg)

### 4.2 Fase de Montagem

![Montagem](/imagem2.jpg)

### 4.3 Fase de Testes

![Testes](/imagem3.jpg)

### 4.4 Funcionamento Final

![Funcionamento](/imagem4.jpg)

---


## 6. Conclusão

---

## 7. Referências
Documentação do Max7219: [Documentação Wokwi](https://docs.wokwi.com/) e  [MicroPython Max7219](https://github.com/mcauser/micropython-max7219l)