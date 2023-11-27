document.getElementById("startRecognitionButton").addEventListener("click", function() {
    fetch('/start-face-recognition', { method: 'GET' })
        .then(response => response.json())
        .then(data => console.log(data));
});

/*
document.getElementById("sendDataButton").addEventListener("click", function() {
    fetch('/clear-sheet', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            const alunos = ['Dani', 'Jao', 'SAM', 'Vini'];
            alunos.forEach(aluno => {
                const dateCell = document.getElementById('date-' + aluno);
                if (dateCell) {
                    dateCell.textContent = 'Aguardando...';
                }
                
                const checkboxContainer = document.getElementById('check-' + aluno);
                checkboxContainer.innerHTML = '<div class="unchecked">✖</div>';
            });
        })
        .catch(error => {
            console.error('Erro ao limpar a planilha:', error);
        });
});
 */

function updateTable() {
    fetch('/get-sheet-data')
        .then(response => response.json())
        .then(data => {
            const alunos = ['Dani', 'Jao', 'SAM', 'Vini'];

            alunos.forEach(aluno => {
                const dateCell = document.getElementById('date-' + aluno);
                const checkCell = document.getElementById('check-' + aluno);
                if (dateCell && checkCell) {
                    dateCell.textContent = 'Aguardando...';
                    checkCell.checked = false;
                }
            });

            data.forEach(([aluno, dataHora]) => {
                const dateCell = document.getElementById('date-' + aluno);
                const checkCell = document.getElementById('check-' + aluno);

                if (dateCell && checkCell) {
                    dateCell.textContent = dataHora;
                    checkCell.checked = true;
                }
            });
        })
        .catch(error => {
            console.error('Erro ao atualizar a tabela:', error);
        });
}

document.addEventListener('DOMContentLoaded', updateTable);

setInterval(updateTable, 100);









