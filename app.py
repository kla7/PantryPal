import streamlit as st
import json
import search
from sentence_transformers import SentenceTransformer
import faiss
import torch
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

torch.classes.__path__ = []

Base = declarative_base()

user_saved_recipes = Table(
    'user_saved_recipes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    saved_recipes = relationship('Recipe', secondary=user_saved_recipes, back_populates='users')
    searches = relationship('SearchHistory', back_populates='user', cascade='all, delete-orphan')


class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    ingredients = Column(String)
    directions = Column(String)
    users = relationship('User', secondary=user_saved_recipes, back_populates='saved_recipes')


class SearchHistory(Base):
    __tablename__ = 'search_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    ingredients = Column(String)
    mode = Column(String)
    restrictions = Column(String)
    avoid = Column(String)

    user = relationship('User', back_populates='searches')


engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

st.title('PantryPal')

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index('search/recipe_index.faiss')
with open('search/recipe_metadata.json', 'r') as f:
    recipes = json.load(f)

ingredients_json = 'cleaned_ingredients.json'
dietary_json = 'dietary_restriction_exclusion_lists.json'

with open(ingredients_json, 'r', encoding='utf-8') as f:
    ingredients = json.load(f)

with open(dietary_json, 'r', encoding='utf-8') as f:
    dietary = json.load(f)

with st.sidebar:
    username = st.text_input('Username', placeholder='Enter your username')
    current_user = None

    if st.button('Login'):
        user = session.query(User).filter_by(username=username).first()
        if user is None:
            user = User(username=username)
            session.add(user)
            session.commit()
            st.toast(f'Welcome, {username}!')
        else:
            st.toast(f'Welcome back, {username}!')
        st.session_state['user_id'] = user.id

    if 'user_id' in st.session_state:
        current_user = session.query(User).filter_by(id=st.session_state['user_id']).first()

        st.markdown('### Saved Recipes')
        saved_titles = [r.title for r in current_user.saved_recipes]

        if saved_titles:
            options = {f'{r.title} (ID: {r.id})': r.id for r in current_user.saved_recipes}
            selected = st.selectbox('Select a recipe to expand', options=options.keys(), index=None)
            if selected:
                selected_id = options[selected]
                selected_recipe = next((r for r in current_user.saved_recipes if r.id == selected_id), None)
                st.session_state['selected_recipe'] = selected_recipe

                if selected_recipe:
                    st.markdown(f'### {selected_recipe.title}')
                    st.markdown(f'**Ingredients:**\n{selected_recipe.ingredients}')
                    st.markdown(f'**Directions:**\n{selected_recipe.directions}')

                    if st.button('Remove', f'remove_{selected_recipe.id}'):
                        current_user.saved_recipes.remove(selected_recipe)
                        session.commit()
                        st.toast('Recipe removed from saved recipes.')
                        st.rerun()
        else:
            st.info('No saved recipes yet.')

search_ingredients = st.multiselect(
        'Ingredients',
        options=ingredients,
        placeholder='Select ingredients'
)
st.session_state['search_ingredients'] = search_ingredients

selection_type = st.radio(
    'Selection type',
    options=['Inclusive', 'Exclusive'],
    index=None,
    horizontal=True,
    help='**Inclusive:** Recipes shown will include ingredients outside of the selected ingredients.\n\n'
         '**Exclusive:** Recipes shown will only contain ingredients from the selected ingredients.'
)
st.session_state['selection_type'] = selection_type

with st.expander('Additional options', expanded=False):
    search_keywords = st.text_input(
        'Search keywords',
        help='Enter keywords, such as "pasta" or "Chinese", for more refined search results.',
        placeholder='Enter keywords here'
    )
    st.session_state['search_keywords'] = search_keywords

    dietary_restrictions = st.multiselect(
        'Dietary Restrictions',
        options=dietary.keys(),
        placeholder='Select dietary restrictions'
    )
    st.session_state['dietary_restrictions'] = dietary_restrictions

    avoid_ingredients = st.multiselect(
        'Avoid list',
        options=ingredients,
        placeholder='Select ingredients to avoid'
    )
    st.session_state['avoid_ingredients'] = avoid_ingredients

for restriction in dietary_restrictions:
    for ingredient in dietary[restriction]:
        avoid_ingredients.append(ingredient)

if st.button('Search'):
    results = search.search_faiss_and_filter(
        model=model,
        index=index,
        recipes=recipes,
        user_ingredients=search_ingredients,
        avoid_ingredients=avoid_ingredients,
        user_keywords=search_keywords,
        mode=selection_type.lower(),
        top_k=10
    )
    st.session_state['search_results'] = results

if 'search_results' in st.session_state:
    for i, result in enumerate(st.session_state['search_results']):
        with st.container(border=1):
            st.subheader(result['title'])
            st.markdown(f'**Ingredients:**\n{result["ingredients"]}')
            st.markdown(f'**Directions:**\n{result["directions"]}')

            if 'user_id' in st.session_state:
                if st.button(f'Save recipe', key=f'save_{i}'):
                    db_recipe = session.query(Recipe).filter_by(title=result['title']).first()
                    if not db_recipe:
                        new_recipe = Recipe(
                            title=result['title'],
                            ingredients=result['ingredients'],
                            directions=result['directions']
                        )
                        session.add(new_recipe)
                        session.commit()
                        db_recipe = new_recipe

                    user = session.query(User).get(st.session_state['user_id'])
                    if db_recipe not in user.saved_recipes:
                        user.saved_recipes.append(db_recipe)
                        session.commit()
                        st.toast('Recipe saved!')
                        st.rerun()
                    else:
                        st.toast('Recipe already saved.')
