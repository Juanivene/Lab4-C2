import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import streamlit as st

# Configuración de la interfaz
st.title('Estimación de Ventas Diarias')
st.sidebar.header('Parámetros de Entrenamiento')

# Parámetros de entrada
learning_rate = st.sidebar.slider('Tasa de aprendizaje', 0.0, 1.0, 0.1, step=0.01)
epochs = st.sidebar.slider('Cantidad de épocas', 10, 10000, 100, step=10)
hidden_neurons = st.sidebar.slider('Neuronas en la capa oculta', 1, 100, 10)

# Botón para entrenar
train_button = st.sidebar.button('Entrenar')

# Leer y preparar datos
data = pd.read_csv('ventas.csv')
scaler = MinMaxScaler()
data['ventas_normalizadas'] = scaler.fit_transform(data[['ventas']])

# Datos de entrenamiento
X = torch.tensor(data['dia'].values, dtype=torch.float32).view(-1, 1)
y = torch.tensor(data['ventas_normalizadas'].values, dtype=torch.float32).view(-1, 1)

# Clase de red neuronal
class VentasNN(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(VentasNN, self).__init__()
        self.hidden = nn.Linear(input_dim, hidden_dim)
        self.output = nn.Linear(hidden_dim, output_dim)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.hidden(x))
        x = self.output(x)
        return x

# Entrenamiento de la red neuronal
if train_button:
    model = VentasNN(input_dim=1, hidden_dim=hidden_neurons, output_dim=1)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    progress_bar = st.progress(0)
    loss_history = []

    for epoch in range(epochs):
        # Forward pass
        predictions = model(X)
        loss = criterion(predictions, y)

        # Backward pass y optimización
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Registro de la pérdida
        loss_history.append(loss.item())

        # Actualizar barra de progreso
        progress_bar.progress((epoch + 1) / epochs)

        # Mostrar pérdida en intervalos
        if epoch % (epochs // 10) == 0 or epoch == epochs - 1:
            st.write(f"Época [{epoch + 1}/{epochs}], Pérdida: {loss.item():.4f}")

    # Desnormalizar las predicciones para graficar
    predictions = scaler.inverse_transform(predictions.detach().numpy().reshape(-1, 1))

    # Gráfica de los resultados
    plt.figure(figsize=(10, 5))
    plt.plot(data['dia'], predictions, label='Predicciones')
    plt.plot(data['dia'], data['ventas'], label='Ventas Reales')
    plt.xlabel('Dia')
    plt.ylabel('Ventas')
    plt.legend()
    st.pyplot(plt)

    # Mensaje final
    st.success("Entrenamiento finalizado exitosamente.")