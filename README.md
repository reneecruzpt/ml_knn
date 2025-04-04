# KNN Machine Learning Application

**Descrição curta**: KNN Machine Learning App: Ferramenta desktop em Python/PyQt5 para pré-processar dados, treinar modelos KNN e prever resultados a partir de CSVs. Inclui visualização, funções personalizadas e undo. Dependências: pandas, scikit-learn, matplotlib. (231 caracteres)

## Sobre o Projeto

A **KNN Machine Learning Application** é uma ferramenta desktop interativa desenvolvida em Python para facilitar o pré-processamento de dados, treinamento de modelos KNN (K-Nearest Neighbors) e previsão de resultados com base em arquivos CSV. Projetada para usuários que desejam explorar e modelar dados tabulares sem escrever código manualmente, oferece uma interface gráfica intuitiva com PyQt5. Ideal para iniciantes em machine learning ou profissionais que buscam uma solução prática.

## Funcionalidades

- **Carregamento de Dados**: Importe CSVs e selecione colunas para análise.
- **Pré-processamento**: Transformações genéricas (ex.: conversão numérica, preenchimento de nulos) e personalizadas (ex.: normalização de datas).
- **Treinamento**: Configure e treine modelos KNN com exibição de acurácia.
- **Previsão**: Preveja resultados para novos clientes individualmente ou em lote.
- **Visualização**: Gráficos comparativos (histogramas/contagens) das colunas.
- **Gerenciamento de Funções**: Crie, edite e exclua funções personalizadas.
- **Histórico**: Desfaça alterações no DataFrame.

## Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal.
- **PyQt5**: Interface gráfica.
- **Pandas**: Manipulação de dados.
- **Scikit-learn**: Modelo KNN e pré-processamento.
- **Matplotlib/Seaborn**: Visualização.
- **Joblib**: Persistência de modelos.

## Estrutura do Projeto

```
pandas_project/
├── ui/
│   ├── main_window.py         # Janela principal e navegação
│   ├── data_manager.py        # Carregamento e validação de dados
│   ├── column_interface.py    # Interação com colunas
│   ├── model_interface.py     # Integração com machine learning
│   ├── utils.py               # Funções utilitárias
│   ├── screens.py             # Configuração das telas
│   ├── details_window.py      # Janela de detalhes das colunas
│   ├── custom_function_manager.py # Gerenciamento de funções personalizadas
│   └── visualization.py       # Visualização de gráficos
├── model.py                   # Lógica de treinamento e previsão
├── preprocessing_custom.py    # Funções personalizadas
├── preprocessing_generic.py   # Funções genéricas
└── main.py                    # Ponto de entrada
```

## Pré-requisitos

- Python 3.8 ou superior
- Dependências:
```
PyQt5>=5.15.9
pandas>=2.0.0
scikit-learn>=1.2.0
matplotlib>=3.7.0
seaborn>=0.12.0
joblib>=1.2.0
```

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/knn-machine-learning-app.git
cd knn-machine-learning-app
```

2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

> Nota: Crie um arquivo `requirements.txt` com as dependências listadas acima, se ainda não existir.

4. Execute a aplicação:
```bash
python main.py
```

## Uso

**Tela 1: Carregue um CSV e selecione colunas para análise.**  
Clique em "Carregar CSV" e escolha um arquivo com a coluna `result`.  
Use a janela de detalhes para pré-processar colunas.

**Tela 2: Treine o modelo KNN.**  
Ajuste o número de vizinhos e clique em "Treinar Modelo".  
Salve ou carregue modelos treinados.

**Tela 3: Preveja resultados.**  
Insira valores manualmente ou carregue um CSV de teste.

### Exemplo de Uso

1. Carregue um CSV com colunas como `id`, `bdate`, `result`.
2. Normalize a coluna `bdate` na janela de detalhes.
3. Treine o modelo com as colunas selecionadas.
4. Gere gráficos ou preveja resultados para novos clientes.

## Contribuições

Contribuições são bem-vindas!  
Abra issues ou envie pull requests com melhorias, correções ou novas funcionalidades.

## Licença

Este projeto está licenciado sob a MIT License (LICENSE).
