import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import os
import json
import base64
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer
import hashlib
import matplotlib
matplotlib.use('Agg')
import xlsxwriter

# Путь к файлу с учетными данными
CREDENTIALS_FILE = 'credentials.json'

# Функция для хеширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Функция для загрузки учетных данных
def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials = json.load(f)
            # Проверяем, правильный ли формат данных
            if 'admin' in credentials and isinstance(credentials['admin'], str):
                return credentials
    # Если файл не существует или данные в неправильном формате, возвращаем начальные учетные данные
    return {"admin": hash_password("admin")}

# Функция для сохранения учетных данных
def save_credentials(credentials):
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f)
    st.write(f"Debug: Credentials saved: {credentials}")

# Функция для авторизации
def authenticate(username, password):
    credentials = load_credentials()
    st.write(f"Debug: Attempting login for user: {username}")
    st.write(f"Debug: Loaded credentials: {credentials}")
    hashed_password = hash_password(password)
    st.write(f"Debug: Hashed input password: {hashed_password}")
    result = username in credentials and credentials[username] == hashed_password
    st.write(f"Debug: Authentication result: {result}")
    return result

# Функция для смены учетных данных
def change_credentials(username, new_password):
    credentials = load_credentials()
    credentials[username] = hash_password(new_password)
    save_credentials(credentials)
    st.success("Учетные данные успешно изменены")

# Функция для загрузки данных
def load_data(period):
    # Здесь должна быть реальная загрузка данных из выбранной директории
    # Для примера используем фиктивные данные и имена файлов
    data = pd.DataFrame({
        'Оператор': ['Оператор 1', 'Оператор 2', 'Оператор 3'] * 10,
        'Дата': pd.date_range(start=period[0], end=period[1], periods=30),
        'Оценка': np.random.randint(1, 6, 30),
        'Ошибки': np.random.randint(0, 5, 30)
    })
    
    # Генерируем фиктивные имена файлов
    file_names = [f"report_{date.strftime('%Y-%m-%d')}.csv" for date in data['Дата'].unique()]
    
    return data, file_names

# Функция для отображения списка загруженных файлов
def display_loaded_files(file_names):
    st.subheader("Загруженные файлы:")
    for file in file_names:
        st.text(file)

# Функция для визуализации данных оператора
def visualize_operator_data(data, operator):
    st.subheader(f"Анализ работы оператора: {operator}")
    
    operator_data = data[data['Оператор'] == operator]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    sns.lineplot(x='Дата', y='Оценка', data=operator_data, ax=ax1)
    ax1.set_title('Динамика оценок')
    ax1.set_ylabel('Оценка')
    
    sns.barplot(x='Дата', y='Ошибки', data=operator_data, ax=ax2)
    ax2.set_title('Количество ошибок')
    ax2.set_ylabel('Ошибки')
    ax2.tick_params(axis='x', rotation=45)
    
    st.pyplot(fig)
    
    avg_score = operator_data['Оценка'].mean()
    total_errors = operator_data['Ошибки'].sum()
    
    st.write(f"Средняя оценка: {avg_score:.2f}")
    st.write(f"Общее количество ошибок: {total_errors}")
    
    if avg_score < 3:
        st.warning("Рекомендация: Необходимо улучшить качество работы.")
    elif avg_score < 4:
        st.info("Рекомендация: Есть потенциал для улучшения.")
    else:
        st.success("Рекомендация: Отличная работа, продолжайте в том же духе!")

# Функция для визуализации данных центра
def visualize_center_data(data):
    st.subheader("Анализ работы центра")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    sns.boxplot(x='Оператор', y='Оценка', data=data, ax=ax1)
    ax1.set_title('Распределение оценок по операторам')
    ax1.set_ylabel('Оценка')
    
    sns.barplot(x='Оператор', y='Ошибки', data=data, ax=ax2)
    ax2.set_title('Общее количество ошибок по операторам')
    ax2.set_ylabel('Ошибки')
    
    st.pyplot(fig)
    
    avg_score = data['Оценка'].mean()
    total_errors = data['Ошибки'].sum()
    
    st.write(f"Средняя оценка центра: {avg_score:.2f}")
    st.write(f"Общее количество ошибок: {total_errors}")
    
    if avg_score < 3:
        st.warning("Рекомендация для центра: Необходимо провести общее обучение персонала.")
    elif avg_score < 4:
        st.info("Рекомендация для центра: Есть потенциал для улучшения работы центра.")
    else:
        st.success("Рекомендация для центра: Центр работает эффективно, продолжайте поддерживать высокий уровень.")

# Функция для создания графиков
def create_charts(data):
    operator_fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    sns.lineplot(x='Дата', y='Оценка', data=data, ax=ax1)
    ax1.set_title('Динамика оценок')
    ax1.set_ylabel('Оценка')
    sns.barplot(x='Дата', y='Ошибки', data=data, ax=ax2)
    ax2.set_title('Количество ошибок')
    ax2.set_ylabel('Ошибки')
    ax2.tick_params(axis='x', rotation=45)
    
    center_fig, (ax3, ax4) = plt.subplots(2, 1, figsize=(10, 12))
    sns.boxplot(x='Оператор', y='Оценка', data=data, ax=ax3)
    ax3.set_title('Распределение оценок по операторам')
    ax3.set_ylabel('Оценка')
    sns.barplot(x='Оператор', y='Ошибки', data=data, ax=ax4)
    ax4.set_title('Общее количество ошибок по операторам')
    ax4.set_ylabel('Ошибки')
    
    return operator_fig, center_fig

# Функция для экспорта данных
def export_data(data, format):
    operator_fig, center_fig = create_charts(data)
    
    if format == 'Excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data.to_excel(writer, index=False, sheet_name='Data')
            workbook = writer.book
            worksheet = writer.sheets['Data']
            
            # Добавляем графики в Excel
            operator_img = BytesIO()
            center_img = BytesIO()
            operator_fig.savefig(operator_img, format='png')
            center_fig.savefig(center_img, format='png')
            worksheet.insert_image('H2', 'operator_chart.png', {'image_data': operator_img})
            worksheet.insert_image('H20', 'center_chart.png', {'image_data': center_img})
            
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="report.xlsx">Скачать отчет Excel</a>'
    elif format == 'PDF':
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        elements.append(Paragraph("Отчет по работе колл-центра", styles['Title']))
        elements.append(Spacer(1, 12))

        # Преобразуем DataFrame в список списков для создания таблицы
        data_list = [data.columns.tolist()] + data.values.tolist()
        t = Table(data_list)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)

        # Добавляем графики в PDF
        operator_img = BytesIO()
        center_img = BytesIO()
        operator_fig.savefig(operator_img, format='png')
        center_fig.savefig(center_img, format='png')
        operator_img.seek(0)
        center_img.seek(0)
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Графики анализа работы оператора", styles['Heading2']))
        elements.append(Image(operator_img, width=400, height=300))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Графики анализа работы центра", styles['Heading2']))
        elements.append(Image(center_img, width=400, height=300))

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        b64 = base64.b64encode(pdf).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="report.pdf">Скачать отчет PDF</a>'

    plt.close(operator_fig)
    plt.close(center_fig)
    st.markdown(href, unsafe_allow_html=True)

# Основная функция приложения
def main():
    st.title("Система нейро-контроля качества для колл-центра")

    st.write(f"Debug: Hash of 'admin': {hash_password('admin')}")

    # Проверка авторизации
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None

    if not st.session_state.authenticated:
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        if st.button("Авторизация"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Авторизация успешна!")
            else:
                st.error("Неверный логин или пароль")
    else:
        st.success(f"Вы авторизованы как {st.session_state.username}")
        
        if st.button("Выйти"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
        
        st.write("Хотите изменить пароль?")
        new_password = st.text_input("Новый пароль", type="password")
        if st.button("Изменить пароль"):
            if new_password:
                change_credentials(st.session_state.username, new_password)
            else:
                st.warning("Пожалуйста, введите новый пароль")

        # Основной интерфейс приложения
        st.sidebar.header("Параметры")

        # Выбор периода
        start_date = st.sidebar.date_input("Начало периода")
        end_date = st.sidebar.date_input("Конец периода")
        if st.sidebar.button("Выбор периода"):
            period = (start_date, end_date)
            st.session_state.data, st.session_state.file_names = load_data(period)
            st.success(f"Данные загружены за период с {start_date} по {end_date}")
            display_loaded_files(st.session_state.file_names)

        # Выбор оператора
        if 'data' in st.session_state:
            operators = st.session_state.data['Оператор'].unique()
            selected_operator = st.sidebar.selectbox("Выбор оператора", operators)
            if st.sidebar.button("Выбор оператора"):
                st.session_state.selected_operator = selected_operator

        # Оценка оператора
        if st.sidebar.button("Оценка оператора"):
            if 'selected_operator' in st.session_state and 'data' in st.session_state:
                visualize_operator_data(st.session_state.data, st.session_state.selected_operator)
            else:
                st.warning("Сначала выберите период и оператора")

        # Оценка центра
        if st.sidebar.button("Оценка центра"):
            if 'data' in st.session_state:
                visualize_center_data(st.session_state.data)
            else:
                st.warning("Сначала выберите период")

        # Экспорт данных
        if 'data' in st.session_state:
            export_format = st.sidebar.selectbox("Формат экспорта", ["Excel", "PDF"])
            if st.sidebar.button("Экспорт данных"):
                export_data(st.session_state.data, export_format)

# Функция для очистки кеша Streamlit
def clear_cache():
    st.cache_data.clear()

if __name__ == "__main__":
    # Добавляем кнопку для очистки кеша
    if st.sidebar.button("Очистить кеш"):
        clear_cache()
        st.success("Кеш очищен")
    
    main()