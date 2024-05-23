import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots



# To deploy, make sure to copy `app.py`, `data` folder, `~.streamlit/sectrets.toml`, and install `requirements.txt`


# # Comment the following line if user/passowrd login is activated!!!!
# st.session_state["username"] = "user"

# This is for user/password login (also need to copy the `~/.streamlit/secrets.toml` file!):
import hmac
def check_password():
    """Returns `True` if the user had a correct password."""
    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            #del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        #return True
        return st.session_state["username"]
    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False
#if not check_password():
#    st.stop()
if check_password():
    st.session_state["username"]=check_password()
else:
    st.stop()




# Set paths
basedir = os.getcwd()
flow_data = pd.read_csv(os.path.join(basedir, 'data/Flow.csv'))
paw_data = pd.read_csv(os.path.join(basedir, 'data/Paw.csv'))
last_index_file = os.path.join(basedir, f'{st.session_state["username"]}_last_index.txt')
labels_file = os.path.join(basedir, f'{st.session_state["username"]}_labels.csv')

# Esto es necesario para que los botones de labels tengan anchura flexible:
st.markdown("""
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
            </style>
            """, unsafe_allow_html=True)


#@st.cache_data
def main():
        
    def save_last_index(current_index, last_index_file):
        with open(last_index_file, 'w') as f:
            f.write(str(current_index))

    def load_last_index():
        if os.path.exists(last_index_file):
            with open(last_index_file, 'r') as f:
                return int(f.read())
        else:
            return 0  # Si el archivo de configuración no existe, comenzar desde el índice 0    
          
    def previous_data(current_index):
        if current_index > 0:
            current_index -= 1
            save_last_index(current_index, last_index_file)  
            #st.rerun()

    def next_data(current_index, flow_data):
        if current_index == len(flow_data)-1:
            current_index = len(flow_data)-1 
            #st.rerun()
        elif current_index < len(flow_data)-1:
            current_index += 1
            save_last_index(current_index, last_index_file)     
            #st.rerun()

    def plot_data(current_index,flow_data,paw_data):
        flow_data_to_plot = flow_data.iloc[current_index, 5:]
        paw_data_to_plot = paw_data.iloc[current_index, 5:]
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,vertical_spacing=0.05)
        fig.add_trace(go.Scatter(y=flow_data_to_plot, mode='lines', name='Flow [L/min]'), row=1, col=1)
        fig.add_trace(go.Scatter(y=paw_data_to_plot, mode='lines', name='Paw [cmH2O]', line=dict(color='red')), row=2, col=1)
        central_region_start = 60  
        central_region_end = (flow_data.iloc[current_index, 3] + flow_data.iloc[current_index, 4]) / 10 + central_region_start - 1
        fig.add_vrect(x0=central_region_start, x1=central_region_end, 
                    fillcolor='lightgreen', opacity=0.3, layer='below', line_width=0,
                    annotation_text='Breath to tag', annotation_position='top',row=1,col=1)
        fig.add_vrect(x0=central_region_start, x1=central_region_end, 
                    fillcolor='lightgreen', opacity=0.3, layer='below', line_width=0,row=2,col=1)
        fig.update_layout(height=500, width=230, showlegend=False, title=f"Breath index: {current_index}")
        fig.update_yaxes(title_text='Flow [L/min]', row=1, col=1)
        fig.update_yaxes(title_text='Paw [cmH2O]', row=2, col=1)
        fig.update_xaxes(title_text='Time [s]', row=2, col=1)
        xticks_short = [(x-60)/20 for x in list(range(0,180,10))]
        fig.update_xaxes(tickvals=[10*x for x in list(range(len(xticks_short)))],ticktext=xticks_short, row=2, col=1)
        #st.plotly_chart(fig, config={'displayModeBar': False})
        st.plotly_chart(fig, config={'displaylogo': False})


    # # Uncomment the following lines (plot_data definition) if esofagic pressure (Peso) is available.
    # # (Basically what this does is to display 3 curves):

    # def plot_data(current_index,flow_data,paw_data):
    #     flow_data_to_plot = flow_data.iloc[current_index, 5:]
    #     paw_data_to_plot = paw_data.iloc[current_index, 5:]
    #     peso_data_to_plot = paw_data.iloc[current_index, 5:]-flow_data.iloc[current_index, 5:]
    #     fig = make_subplots(rows=3, cols=1, shared_xaxes=True,vertical_spacing=0.05)
    #     fig.add_trace(go.Scatter(y=flow_data_to_plot, mode='lines', name='Flow [L/min]'), row=1, col=1)
    #     fig.add_trace(go.Scatter(y=paw_data_to_plot, mode='lines', name='Paw [cmH2O]', line=dict(color='red')), row=2, col=1)
    #     fig.add_trace(go.Scatter(y=peso_data_to_plot, mode='lines', name='Peso [cmH2O]', line=dict(color='green')), row=3, col=1)
    #     central_region_start = 60  
    #     central_region_end = (flow_data.iloc[current_index, 3] + flow_data.iloc[current_index, 4]) / 10 + central_region_start - 1
    #     fig.add_vrect(x0=central_region_start, x1=central_region_end, 
    #                 fillcolor='lightgreen', opacity=0.3, layer='below', line_width=0,
    #                 annotation_text='Breath to tag', annotation_position='top',row=1,col=1)
    #     fig.add_vrect(x0=central_region_start, x1=central_region_end, 
    #                 fillcolor='lightgreen', opacity=0.3, layer='below', line_width=0,row=2,col=1)
    #     fig.add_vrect(x0=central_region_start, x1=central_region_end, 
    #                 fillcolor='lightgreen', opacity=0.3, layer='below', line_width=0,row=3,col=1)
    #     fig.update_layout(height=570, width=630, showlegend=False, title=f"Breath index: {current_index}")
    #     fig.update_yaxes(title_text='Flow [L/min]', row=1, col=1)
    #     fig.update_yaxes(title_text='Paw [cmH2O]', row=2, col=1)
    #     fig.update_yaxes(title_text='Peso [cmH2O]', row=3, col=1)
    #     fig.update_xaxes(title_text='Time [s]', row=3, col=1)
    #     xticks_short = [(x-60)/20 for x in list(range(0,180,10))]
    #     fig.update_xaxes(tickvals=[10*x for x in list(range(len(xticks_short)))],ticktext=xticks_short, row=3, col=1)
    #     #st.plotly_chart(fig, config={'displayModeBar': False})
    #     st.plotly_chart(fig, config={'displaylogo': False})

          
    def label_data(label,current_index,flow_data,labels_file):
        df_labels = pd.DataFrame(columns=['id', 'label'])
        if os.path.exists(labels_file):
            df_labels = pd.read_csv(labels_file)
        df_labels = df_labels[df_labels['id'] != flow_data.iloc[current_index, 0]]
        new_row = pd.DataFrame({'id': [flow_data.iloc[current_index, 0]-1], 'label': [label]})
        df_labels = pd.concat([df_labels, new_row], ignore_index=True)
        df_labels.to_csv(labels_file, index=False)
        next_data(current_index, flow_data)  
    
    def submit():
        if not st.session_state.widget.isnumeric():
            st.error("Not a valid input, please provide a valid index value.")
        elif ((st.session_state.widget.isnumeric()) & (int(st.session_state.widget) >=0) & (int(st.session_state.widget) < len(flow_data))):
            st.session_state.my_text = st.session_state.widget    
            st.session_state.widget = ""
            current_index = int(st.session_state.my_text)
            save_last_index(current_index, last_index_file) 
        else:
             st.error("Not a valid input, please provide a valid index value.") 


    # Initialize breath index
    current_index = load_last_index()         
          
    # Sidebar
    st.sidebar.title(f"Welcome {st.session_state["username"]}")
    st.sidebar.caption(":gray[Label each breath by clicking one of the buttons below the graph. When a button is pressed, the next breath will be automatically displayed.]")
    st.sidebar.caption(":gray[You can close this app at any time, the last displayed breath will be shown when reopening the app.]")
    st.sidebar.markdown("___")
    st.sidebar.caption(":gray[Use these buttons to display the previous or next breath, if necessary:]")
    # if st.sidebar.button("Previous breath"):
    #     previous_data(current_index)
    # if st.sidebar.button("Next breath"):
    #     next_data(current_index, flow_data)  
    if "button_sb1" not in st.session_state:
        st.session_state.button_sb1 = 1
    if "button_sb2" not in st.session_state:
        st.session_state.button_sb2 = 1
    def buttonsb1_pressed():
        st.session_state.button_sb1 += 1
        previous_data(current_index)
    def buttonsb2_pressed():
        st.session_state.button_sb2 += 1
        next_data(current_index, flow_data)
    st.sidebar.button("Previous breath",on_click=buttonsb1_pressed,key=f"buttonsb1_{st.session_state.button_sb1}")
    st.sidebar.button("Next breath",on_click=buttonsb2_pressed,key=f"buttonsb2_{st.session_state.button_sb2}")
    st.sidebar.markdown("")   
    
    if "my_text" not in st.session_state:
        st.session_state.my_text = ""  
    st.sidebar.text_input(f":gray[Otherwise, write the breath index to display (integer between 0 and {len(flow_data)-1}):]", key="widget", on_change=submit)

    # Uncomment the following lines to add a "Donwload data" button:
    st.sidebar.markdown("___")
    if os.path.exists(labels_file):
        st.sidebar.caption(":gray[Press the button below to download the tagged breaths (as a `.csv` file):]")
        st.sidebar.download_button(label="Download tagged breaths",data=pd.read_csv(labels_file).to_csv(index=False),file_name=labels_file,mime='text/csv') 


    # Plot
    plot_data(current_index, flow_data, paw_data)
    

    # Labels buttons
    colb1, colb2, colb3, colb4, colb5, colb6, colb7, colb8, colb9 = st.columns([1,1,1,1,1,1,1,1,1])

    if "button_b1" not in st.session_state:
        st.session_state.button_b1 = 1
    if "button_b2" not in st.session_state:
        st.session_state.button_b2 = 1
    if "button_b3" not in st.session_state:
        st.session_state.button_b3 = 1
    if "button_b4" not in st.session_state:
        st.session_state.button_b4 = 1
    if "button_b5" not in st.session_state:
        st.session_state.button_b5 = 1
    if "button_b6" not in st.session_state:
        st.session_state.button_b6 = 1
    if "button_b7" not in st.session_state:
        st.session_state.button_b7 = 1
    if "button_b8" not in st.session_state:
        st.session_state.button_b8 = 1
    if "button_b9" not in st.session_state:
        st.session_state.button_b9 = 1
    
    def buttonb1_pressed():
        st.session_state.button_b1 += 1
        label_data("Normal",current_index,flow_data,labels_file)
    def buttonb2_pressed():
        st.session_state.button_b2 += 1
        label_data("DT",current_index,flow_data,labels_file)
    def buttonb3_pressed():
        st.session_state.button_b3 += 1
        label_data("IE",current_index,flow_data,labels_file)
    def buttonb4_pressed():
        st.session_state.button_b4 += 1
        label_data("SC",current_index,flow_data,labels_file)
    def buttonb5_pressed():
        st.session_state.button_b5 += 1
        label_data("PC",current_index,flow_data,labels_file)
    def buttonb6_pressed():
        st.session_state.button_b6 += 1
        label_data("RT-DT",current_index,flow_data,labels_file)
    def buttonb7_pressed():
        st.session_state.button_b7 += 1
        label_data("RTinsp",current_index,flow_data,labels_file)
    def buttonb8_pressed():
        st.session_state.button_b8 += 1
        label_data("RTexp",current_index,flow_data,labels_file)
    def buttonb9_pressed():
        st.session_state.button_b9 += 1
        label_data("Others",current_index,flow_data,labels_file)

    colb1.button("Normal",on_click=buttonb1_pressed,key=f"buttonb1_{st.session_state.button_b1}")
    colb2.button("DT",on_click=buttonb2_pressed,key=f"buttonb2_{st.session_state.button_b2}")
    colb3.button("IE",on_click=buttonb3_pressed,key=f"buttonb3_{st.session_state.button_b3}")
    colb4.button("SC",on_click=buttonb4_pressed,key=f"buttonb4_{st.session_state.button_b4}")
    colb5.button("PC",on_click=buttonb5_pressed,key=f"buttonb5_{st.session_state.button_b5}")
    colb6.button("RT-DT",on_click=buttonb6_pressed,key=f"buttonb6_{st.session_state.button_b6}")
    colb7.button("RTinsp",on_click=buttonb7_pressed,key=f"buttonb7_{st.session_state.button_b7}")
    colb8.button("RTexp",on_click=buttonb8_pressed,key=f"buttonb8_{st.session_state.button_b8}")
    colb9.button("Others",on_click=buttonb9_pressed,key=f"buttonb9_{st.session_state.button_b9}")

if __name__ == "__main__":
    main()