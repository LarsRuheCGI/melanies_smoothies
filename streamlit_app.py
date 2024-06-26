# Import python packages
import streamlit as st
import numpy as np
from snowflake.snowpark.functions import col
import requests

cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie
    """
)

name_one_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_one_order)


my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
pd_df = my_dataframe.to_pandas()



ingredients_list = st.multiselect("What is your favorite fruit?", 
                                  my_dataframe,
                                  max_selections= 5)

time_to_insert = st.button('Submit Order')

if time_to_insert:
    ingredients_string = ""
    for ingredient in ingredients_list:
        ingredients_string += ingredient + " "

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == ingredient, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', ingredient,' is ', search_on, '.')
        
        st.subheader(ingredient + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """','""" + name_one_order + """')"""
    
    st.write(my_insert_stmt)
    
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon = "✅")
