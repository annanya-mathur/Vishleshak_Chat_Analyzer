import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import tempfile
import emoji

# Function to parse messages in the chat file
def parse_message(message):
    # Split the message into date, time, sender, and content
    try:
        date_time, content = message.split(' - ')
        date_time = datetime.strptime(date_time, '%d/%m/%y, %I:%M %p')
        sender, content = content.split(': ', 1)
    except ValueError:
        date_time = None
        sender = 'Unknown'
        content = message
    return {'date': date_time.date() if date_time else None, 'time': date_time.time() if date_time else None, 'sender': sender, 'content': content}

# Function to load and parse the chat file
def load_chat(file):
    with open(file.name, 'r', encoding='utf-8') as f:
        messages = f.read().split('\n')
    messages = [parse_message(m) for m in messages if len(m) > 0]
    return pd.DataFrame(messages)

# Function to calculate message statistics
def calculate_statistics(df):
    total_messages = df.shape[0]
    senders = df['sender'].unique()
    sender_counts = df['sender'].value_counts()
    most_active_sender = sender_counts.index[0]
    messages_per_day = df.groupby('date').size().mean()
    return {'total_messages': total_messages, 'senders': senders, 'sender_counts': sender_counts, 'most_active_sender': most_active_sender, 'messages_per_day': messages_per_day}

# Function to display message statistics
def display_statistics(stats):
    st.write('*Total messages:*', stats['total_messages'])
    st.write('*Senders:*', ', '.join(stats['senders']))
    st.write('*Sender counts:*')
    for sender, count in stats['sender_counts'].items():
        st.write('- {}: {}'.format(sender, count))
    st.write('*Most active sender:*', stats['most_active_sender'])
    st.write('*Messages per day:* {:.2f}'.format(stats['messages_per_day']))

# Function to display emojis
# Function to display emojis
# Function to display emojis
def display_emojis(df):
    emojis = []
    for content in df['content']:
        emojis += [emoji_info['emoji'] for emoji_info in emoji.emoji_list(content)]
    unique_emojis = set(emojis)
    st.write('*Emojis used:*', ', '.join(unique_emojis))

# Function to find the most commonly used emoji
def find_most_common_emoji(df):
    emojis = []
    for content in df['content']:
        emojis += emoji.emoji_list(content)
    emoji_counts = pd.Series(emojis).value_counts()
    most_common_emoji = emoji_counts.index[0]
    st.write('*Most commonly used emoji:*', most_common_emoji)


def display_most_active_users_heatmap(df):
    active_users = df['sender'].value_counts().head(10).index.tolist()
    df_active_users = df[df['sender'].isin(active_users)]
    pivot_df = df_active_users.pivot_table(index=df_active_users['date'].dt.month, columns='sender', aggfunc='size',
                                           fill_value=0)
    pivot_df.columns = pivot_df.columns.map(lambda x: calendar.month_abbr[int(x)] if isinstance(x, (int, float)) else x)

    # Format numeric columns
    pivot_df = pivot_df.applymap(lambda x: f"{x:,}" if isinstance(x, int) else x)

    st.write('**Most Active Users Heatmap:**')
    st.dataframe(pivot_df)


# Streamlit app
def main():
    st.title('WhatsApp Chat Analyzer')

    # Upload file
    file = st.file_uploader('Upload chat file (.txt)', type='txt')
    if not file:
        return

    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.read())

    # Load and parse chat file
    df = load_chat(temp_file)

    # Calculate and display statistics
    stats = calculate_statistics(df)
    st.header('Statistics')
    display_statistics(stats)

    # Display emojis
    st.header('Emojis')
    display_emojis(df)

    # Find most commonly used emoji
    st.header('Most Common Emoji')
    find_most_common_emoji(df)
    

    # Display messages table
    st.header('Messages')
    st.dataframe(df)

if __name__ == '__main__':
    main()