"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest
from django.shortcuts import render, redirect 
from django.contrib import messages
from app.models import student
from app.models import prompts_ai
from app.models import prompts_list
from django.db import connection
from django.http import HttpResponse
from django.http import JsonResponse
from EdgeGPT.EdgeUtils import Chatbot, Query, Cookie
from EdgeGPT.EdgeGPT import ConversationStyle
import replicate
import asyncio
import os
import time
import re
import json
import textwrap
import pandas as pd


import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist
from nltk.corpus import wordnet
from nltk import FreqDist
import string
import gensim
import random
from gensim import corpora
from collections import defaultdict
from nltk.util import ngrams
from collections import Counter







# api_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from app.serializers import studentSerializer
from app.serializers import LoginSerializer
from app.serializers import promptSerializer
from app.serializers import promptlistSerializer
from django.views.decorators.csrf import csrf_exempt

os.environ['REPLICATE_API_TOKEN'] = 'r8_cBwvede14r3poOmt9WAQoBD6nTiLo0602eIaJ'


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['uname']
        password = serializer.validated_data['pswd']
        student_data = student.objects.all()


        try:
            output = replicate.run(
                "replicate/llama-2-70b-chat:58d078176e02c219e11eb4da5a02a7830a283b14cf8f94537af893ccff5ee781",
                input={"prompt": "who is the president of United States?"}
            )


            for item in output:
                 print(item)
        except Exception as e:
            print("An error occurred:", e)





        

        if any(stack.uname == username and stack.pswd == password for stack in student_data):
            # Authentication successful, create session for the user
            

             # Return the response with the username (session data value)
            return Response({'message': 'Login successful', 'username': username}, status=status.HTTP_200_OK)
        else:
            # Authentication failed
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)






   
        




class ProcessPromptAPIView(APIView):
    
    def post(self, request):
        
        data = request.data
        prompt = data.get('prompt')
        username_s = data.get('username')
        print(username_s)
        

        

        
        prompt_ap="||-||"+ prompt


        query = '''
        UPDATE railway.prompts
        SET prompt = CONCAT(COALESCE(prompt, ''), %s)
        WHERE id IN (
            SELECT row_num
            FROM (
                SELECT uname, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as row_num
                FROM railway.studenttb
            ) AS numbered_rows
            WHERE uname = %s
            );


        '''

    # Execute the query using Django's database connection
        with connection.cursor() as cursor:
            cursor.execute(query, [prompt_ap, username_s])
            rows_updated = cursor.rowcount


        print("Rows Updated:", rows_updated) 

        prompt_p=prompt

        
        prompt=prompt+",wrap the entire answer between +++ +++"
           
        
        print("line 146")

        async def main(prompt):
            try:
                cookies = json.loads(open("bing_cookies_.json", encoding="utf-8").read())
                bot = await Chatbot.create(cookies=cookies)
                result = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative)
                await bot.close()
                return json.dumps(result)
    
            except Exception as e:
                print("Error:", e)
                return None


        
        data = str(json.loads(asyncio.run(main(prompt))))

        print(data)
       
        
       
       


        results = re.findall(r'\+\+\+(.*?)\+\+\+', data)
        results=[promp for promp in results if promp.strip()]
       

        result_string = results[0]

        formatted_string = result_string.replace(r'\n', '\n')


        bot_response = formatted_string
        print(bot_response)
        


        response_data = {
            'user':username_s,
            'user_message': prompt_p,
            'processed_message': bot_response,
        }
        
        print("line 171")
        return Response(response_data, status=status.HTTP_200_OK)





         
class ProcessJsonAPIView(APIView):
    
    def get(self, request):
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM prompts ;")
            results = cursor.fetchall()
            column_names = cursor.fetchallcolumn_names = [col[0] for col in cursor.description]

        df1 = pd.DataFrame(results, columns=column_names)  


        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM studenttb ;")
            results = cursor.fetchall()
            column_names = cursor.fetchallcolumn_names = [col[0] for col in cursor.description]

        df2 = pd.DataFrame(results, columns=column_names)  


        df_c=pd.concat([df1,df2],axis=1)
        df = df_c.dropna(subset=['prompt'])
        df_f=df[['uname', 'prompt']]

        store=[]
        fstore=[]
        all_emo=[]
        for pro in df_f.prompt:
            
            div = pro.split("||-||")
            split_text=[promp for promp in div if promp.strip()]

            combined_text = " ".join(split_text)
            combined_text=combined_text.lower()
            tokens_bi = word_tokenize(combined_text)
            stop_words = set(word.lower().translate(str.maketrans('', '', string.punctuation)) for word in stopwords.words('english'))
            tokens_bi = [token for token in tokens_bi if token not in stop_words]
            

        
        

            # Tokenization
            tokens = [word_tokenize(prompt) for prompt in split_text]
        


            # Remove punctuation from stop words
            stop_words = set(word.lower().translate(str.maketrans('', '', string.punctuation)) for word in stopwords.words('english'))

            # Remove stopwords and punctuation for each sentence
            filtered_tokens_list = [
                [word.lower() for word in token if word.lower() not in stop_words and word not in string.punctuation]
                for token in tokens
            ]


            # Sentiment Analysis
            sentiment_analyzer = SentimentIntensityAnalyzer()
            sentiments = [sentiment_analyzer.polarity_scores(prompt) for prompt in split_text]
            all_emo.append(sentiments)

            # Calculate the average sentiment scores
            num_prompts = len(split_text)
            total_sentiments = {
                'neg': sum(sentiment['neg'] for sentiment in sentiments),
                'neu': sum(sentiment['neu'] for sentiment in sentiments),
                'pos': sum(sentiment['pos'] for sentiment in sentiments),
                'compound': sum(sentiment['compound'] for sentiment in sentiments)
            }

            average_sentiments = {
                'neg': round(total_sentiments['neg'] / num_prompts,2),
                'neu': round(total_sentiments['neu'] / num_prompts,2),
                'pos': round(total_sentiments['pos'] / num_prompts,2),
                'compound': round(total_sentiments['compound'] / num_prompts,2)
            }



            flat_tokens = [word for token in filtered_tokens_list for word in token]
            freq_dist = FreqDist(flat_tokens)
            fstore.append(freq_dist.most_common(3))
            store.append(average_sentiments)



            # Function to generate N-grams
            def generate_ngrams(token_list, n):
                return list(ngrams(token_list, n))

            
            def generate_bigrams(token_list):
                return generate_ngrams(token_list, 2)
            

            bigrams_combined_text = generate_bigrams(tokens_bi)

            bigram_freq = Counter(bigrams_combined_text)

            # Sort the bigrams based on frequency in descending order
            sorted_bigrams = sorted(bigram_freq.items(), key=lambda item: item[1], reverse=True)

            # Select the top N most frequently occurring bigrams
            top_n = 5
            most_common_bigrams = sorted_bigrams[:top_n]

            print("Top {} most frequently occurring bigrams:".format(top_n))
            for bigram, frequency in most_common_bigrams:
                print(f"{bigram}: {frequency} times")



            
           




            
            
        data_strings = [str(item) for item in fstore]
        df_FR = pd.DataFrame({'WordFrequency': data_strings})
        df_SA=pd.DataFrame(store)
        

        def get_emotion_label(compound_score):
            if compound_score >= 1:
                return 'Highly Positive'
            elif compound_score >= 0.5 and compound_score < 1:
                return 'Positive'
            elif compound_score <= -1:
                return 'Highly Negative'
            elif compound_score <= -0.5 and compound_score > -1:
                return 'Negative'
            else:
                return 'Neutral'

        # Apply the function to create a new 'Emotion' column
        df_SA['Emotion'] = df_SA['compound'].apply(get_emotion_label)
       


        data_strings_emo = [str(item) for item in all_emo]
        df_emo = pd.DataFrame({'All_emotions': data_strings_emo})
        



        df1_reset = df_f.reset_index(drop=True)
        df2_reset = df_SA.reset_index(drop=True)
        df3_reset=df_FR.reset_index(drop=True)
        df4_reset=df_emo.reset_index(drop=True)

        result=pd.concat([df1_reset,df2_reset,df3_reset,df4_reset],axis=1)
        result['WordFrequency'] = result['WordFrequency'].str.replace(r'[()\[\]\'"]', '', regex=True)
        result['All_emotions'] = result['All_emotions'].str.replace(r"'|,|{|}", '', regex=True)
        json_records = result.to_json(orient='records')
        
        

        return Response(json_records, status=status.HTTP_200_OK)
    

class GeneratePromptsView(APIView):
    def get(self, request):
        username = request.query_params.get('username', '')

        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM prompts ;")
            results = cursor.fetchall()
            column_names = cursor.fetchallcolumn_names = [col[0] for col in cursor.description]

        df1 = pd.DataFrame(results, columns=column_names)  


        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM studenttb ;")
            results = cursor.fetchall()
            column_names = cursor.fetchallcolumn_names = [col[0] for col in cursor.description]

        df2 = pd.DataFrame(results, columns=column_names)  


        df_c=pd.concat([df1,df2],axis=1)
        df = df_c.dropna(subset=['prompt'])
        df_f=df[['uname', 'prompt']]

        # Boolean indexing to filter rows based on 'uname' column
        filtered_rows = df[df['uname'] == username]

        # Get one of the elements from the 'prompts' column based on the filtered row(s)
        desired_prompt = filtered_rows['prompt'].iloc[0] 

        div = desired_prompt.split("||-||")
        split_text=[promp for promp in div if promp.strip()]

  

        combined_text = " ".join(split_text)
        combined_text=combined_text.lower()
        combined_text = combined_text.replace("''", "").replace("``", "")
        combined_text= " ".join(combined_text.split())
        n_stop=word_tokenize(combined_text)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in n_stop if word.lower() not in stop_words]
        filtered_words=[token for token in filtered_words if token not in string.punctuation]
        
        
       
        
       

        def generate_ngrams(token_list, n):
                return list(ngrams(token_list, n))

            
        def generate_bigrams(token_list):
                return generate_ngrams(token_list, 2)
        
        
            

        print(filtered_words)
        bigrams_combined_text = generate_bigrams(filtered_words)

        bigram_freq = Counter(bigrams_combined_text)
        sorted_bigrams = sorted(bigram_freq.items(), key=lambda item: item[1], reverse=True)
        top_n = 20
        most_common_bigrams = sorted_bigrams[:top_n]
        Bi_g=[]
        for bigram, frequency in most_common_bigrams:
             Bi_g.append(" ".join(bigram))
        print(Bi_g)
        #Bot Build     
        Bi_choice=random.choice(Bi_g)
        prompt="Generate multiple random prompts that is rich in detail based on the topic {}, wrap the question between ** **".format(Bi_choice)   
        print(prompt)        
        data = str(json.loads(asyncio.run(main(prompt))))
        
        
       


        results = re.findall(r'\*\*(.*?)\*\*', data)
        results=[promp for promp in results if promp.strip()]
        

        result_string = random.choice(results)
        bot_response = result_string
        
        prompts = result_string

        return Response({'prompts': prompts})






    
    
   










