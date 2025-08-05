import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go


# --- Отображение графика ---

def plot_interactive_sentiment(df, lang="ru"):
    # Маппинг
    sentiment_to_mood = {'negative': 1, 'neutral': 2, 'positive': 4}
    df['mood'] = df['sentiment'].map(sentiment_to_mood)
    df['date'] = pd.to_datetime(df['date']).dt.date

    mood_by_day = df.groupby('date')['mood'].mean()
    today = datetime.today().date()
    last_7_days = pd.date_range(end=today, periods=7).date
    mood_by_day = mood_by_day.reindex(last_7_days, fill_value=0)

    # Переводы
    translations = {
        'en': {
            'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'mood_labels': ['Bad', 'Okay', 'Good', 'Excellent'],
            'title': 'Weekly Mood',
        },
        'ru': {
            'days': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
            'mood_labels': ['Плохо', 'Нормально', 'Хорошо', 'Отлично'],
            'title': 'Настроение за неделю',
        },
        'kk': {
            'days': ['Дс', 'Сс', 'Ср', 'Бс', 'Жм', 'Сб', 'Жс'],
            'mood_labels': ['Нашар', 'Орташа', 'Жақсы', 'Өте жақсы'],
            'title': 'Апта бойғы көңіл күй',
        }
    }

    svg_icon = '''
    <svg xmlns="http://www.w3.org/2000/svg" height="30px" viewBox="0 -960 960 960" width="30px" fill="#e3e3e3" style="vertical-align: middle;">
    <path d="M108-255q-12-12-11.5-28.5T108-311l211-214q23-23 57-23t57 23l103 104 208-206h-64q-17 0-28.5-11.5T640-667q0-17 11.5-28.5T680-707h160q17 0 28.5 11.5T880-667v160q0 17-11.5 28.5T840-467q-17 0-28.5-11.5T800-507v-64L593-364q-23 23-57 23t-57-23L376-467 164-255q-11 11-28 11t-28-11Z"/>
    </svg>
    '''

    # Displaying the title with SVG above the chart
    st.markdown(f"<h3>{svg_icon} {translations[lang]['title']}</h3>", unsafe_allow_html=True)

    mood_df = pd.DataFrame({'date': mood_by_day.index, 'mood': mood_by_day.values})
    mood_df['day_name'] = [translations[lang]['days'][d.weekday()] for d in mood_df['date']]

    # Преобразование чисел в текст
    def mood_to_text(mood_val):
        if 0 <= mood_val <= 1:
            return translations[lang]['mood_labels'][0]
        elif 1 < mood_val <= 2:
            return translations[lang]['mood_labels'][1]
        elif 2 < mood_val <= 3:
            return translations[lang]['mood_labels'][2]
        elif 3 < mood_val <= 4:
            return translations[lang]['mood_labels'][3]
        else:
            return ""

    mood_df['text_mood'] = mood_df['mood'].apply(mood_to_text)

    # Создание графика
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mood_df['day_name'],
        y=mood_df['mood'],
        mode='lines+markers+text',
        text=mood_df['text_mood'],
        textposition='top center',
        line=dict(color='mediumpurple', width=3),
        marker=dict(size=10),
        hovertext=[
        f"({day}, {date.day})<br>{mood}"
        for date, day, mood in zip(mood_df['date'], mood_df['day_name'], mood_df['text_mood'])
    ],
        hoverinfo="text"
    ))

    # Обновление осей
    fig.update_layout(
        title='',
        xaxis_title='',
        yaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4],
            ticktext=translations[lang]['mood_labels'],
            range=[0, 4.1]
        ),
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
