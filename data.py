import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import tempfile
import emoji
import calendar

# Function to parse messages in the chat file

def parse_message(message):
    message_parts = message.split(' - ')
    if len(message_parts) > 1:
        timestamp_str, content = message_parts
        timestamp = datetime.strptime(timestamp_str, "%d/%m/%y, %I:%M %p")
        return {'Timestamp': timestamp, 'Content': content}
    return {}

# Function to load the chat data from a file
def load_chat(file):
    with open(file, 'r', encoding='utf-8') as f:
        messages = f.readlines()

    messages = [parse_message(m) for m in messages if len(m) > 0]
    messages = [m for m in messages if m]

    df = pd.DataFrame(messages)
    df['Sender'] = df['Content'].apply(lambda x: x.split(':')[0].strip())
    df['Content'] = df['Content'].apply(lambda x: x.split(': ', 1)[1].strip())

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date

    return df







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
    st.markdown('**Total messages:**')
    st.markdown('<p style="font-size:20px; line-height:1.5;">{}</p>'.format(stats['total_messages']), unsafe_allow_html=True)

    st.markdown('**Senders:**')
    st.markdown('<p style="font-size:20px; line-height:1.5;">{}</p>'.format(', '.join(stats['senders'])), unsafe_allow_html=True)

    st.markdown('**Sender counts:**')
    for sender, count in stats['sender_counts'].items():
        st.markdown('- {}: {}'.format(sender, count))

    st.markdown('**Most active sender:**')
    st.markdown('<p style="font-size:20px; line-height:1.5;">{}</p>'.format(stats['most_active_sender']), unsafe_allow_html=True)

    st.markdown('**Messages per day:**')
    st.markdown('<p style="font-size:20px; line-height:1.5;">{:.2f}</p>'.format(stats['messages_per_day']), unsafe_allow_html=True)

# Function to display emojis
def display_emojis(df):
    emojis = []
    for content in df['content']:
        emojis += [emoji_info['emoji'] for emoji_info in emoji.emoji_list(content)]
    unique_emojis = set(emojis)
    st.markdown('**Emojis used:**')
    st.markdown('<p style="font-size:30px; line-height:1.5;">{}</p>'.format(', '.join(unique_emojis)), unsafe_allow_html=True)

# Function to find the most commonly used emoji
def find_most_common_emoji(df):
    emojis = []
    for content in df['content']:
        emojis += [emoji_info['emoji'] for emoji_info in emoji.emoji_list(content)]
    emoji_counts = pd.Series(emojis).value_counts()
    most_common_emoji = emoji_counts.index[0]
    st.markdown('**Most common emoji:**')
    st.markdown('<p style="font-size:20px; line-height:1.5;">{}</p>'.format(most_common_emoji), unsafe_allow_html=True)

def main():
    st.title("WhatsApp Chat Analyzer")

    # File uploader
    st.sidebar.header('Upload your WhatsApp chat file')
    file = st.sidebar.file_uploader('Upload .txt file', type=['txt'])
    if not file:
        st.info('Please upload a WhatsApp chat file.')
        return



    # File upload
    uploaded_file = st.file_uploader("Upload your WhatsApp chat file (.txt)", type="txt")

    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.read())
        temp_file.close()

        # Load the chat data from the file
        df = load_chat(temp_file.name)

        # Remove the temporary file
        os.remove(temp_file.name)
    # Calculate statistics
    stats = calculate_statistics(df)

    # Display statistics
    st.header('Chat Statistics')
    display_statistics(stats)

    # Find most commonly used emoji
    st.header('Most Common Emoji')
    find_most_common_emoji(df)

    # Display messages table
    st.header('Messages')
    st.dataframe(df.style.set_properties(**{'text-align': 'left', 'white-space': 'pre-wrap'}))

    # Display emojis
    st.header('Emojis')
    display_emojis(df)

def display_statistics(stats):
    st.markdown('**Total messages:**')
    st.markdown('<p style="font-size:30px; line-height:1.5;">{}</p>'.format(stats['total_messages']), unsafe_allow_html=True)

    st.markdown('**Senders:**')
    st.markdown('<p style="font-size:30px; line-height:1.5;">{}</p>'.format(', '.join(stats['senders'])), unsafe_allow_html=True)

    st.markdown('**Sender counts:**')
    fig, ax = plt.subplots()
    ax.bar(stats['sender_counts'].index, stats['sender_counts'].values)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    st.markdown('**Most active month:**')
    st.markdown('<p style="font-size:30px; line-height:1.5;">{}</p>'.format(stats['most_active_month']),
                unsafe_allow_html=True)

    st.markdown('**Monthly message counts:**')
    fig, ax = plt.subplots()
    ax.plot(stats['monthly_counts'].index, stats['monthly_counts'].values)
    ax.set_xlabel('Month')
    ax.set_ylabel('Message Count')
    ax.set_xticks(stats['monthly_counts'].index)
    ax.set_xticklabels([calendar.month_abbr[i] for i in stats['monthly_counts'].index])
    ax.set_title('Monthly Message Counts')
    st.pyplot(fig)

if __name__ == '__main__':
    main()
