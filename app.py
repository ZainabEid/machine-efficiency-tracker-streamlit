"""
Machine Efficiency Tracker - Streamlit Application
Main application for monitoring machine status, efficiency, and productivity
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db_handler import DatabaseHandler
from utils.calculations import EfficiencyCalculator
from utils.data_generator import DataGenerator
import config
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Machine Efficiency Tracker",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def init_db():
    return DatabaseHandler(config.DB_PATH)

db = init_db()
calc = EfficiencyCalculator()

# Sidebar
st.sidebar.title("⚙️ Machine Efficiency Tracker")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "📍 Navigation",
    ["📊 Dashboard", "🤖 Machine Details", "📝 Add Log", "➕ Add Machine", 
     "📈 Analytics", "🎲 Generate Sample Data"]
)

st.sidebar.markdown("---")

# Date range filter
st.sidebar.subheader("📅 Date Range")
end_date = datetime.now().date()
start_date = end_date - timedelta(days=7)
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(start_date, end_date),
    max_value=end_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range[0]
    end_date = start_date

st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 About")
st.sidebar.info(
    "Track machine efficiency, monitor status, "
    "and analyze productivity metrics in real-time."
)

# Main content based on page selection
if page == "📊 Dashboard":
    st.title("📊 Machine Efficiency Dashboard")
    st.markdown(f"**Date Range:** {start_date} to {end_date}")
    
    # Get all machines
    machines_df = db.get_all_machines()
    
    if machines_df.empty:
        st.warning("⚠️ No machines found in the database!")
        st.info("👉 Go to **'➕ Add Machine'** or **'🎲 Generate Sample Data'** to get started.")
    else:
        # Overall metrics
        st.subheader("📈 Overall Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_machines = len(machines_df)
        logs_df = db.get_machine_logs(start_date=str(start_date), end_date=str(end_date))
        failures_df = db.get_failures(start_date=str(start_date), end_date=str(end_date))
        
        with col1:
            st.metric("🤖 Total Machines", total_machines)
        
        with col2:
            avg_efficiency = calc.calculate_running_time_percentage(logs_df)
            delta_color = "normal" if avg_efficiency >= config.MIN_EFFICIENCY else "inverse"
            st.metric("⚡ Avg Running Time", f"{avg_efficiency:.1f}%")
        
        with col3:
            failure_rate = calc.calculate_daily_failure_rate(failures_df)
            st.metric("⚠️ Avg Daily Failures", f"{failure_rate['avg_failures_per_day']:.1f}")
        
        with col4:
            productivity = calc.calculate_productivity(logs_df)
            st.metric("📦 Production/Hour", f"{productivity['production_per_hour']:.1f}")
        
        st.markdown("---")
        
        # Machine-wise status
        st.subheader("🤖 Machine Status Overview")
        
        machine_metrics = []
        for _, machine in machines_df.iterrows():
            machine_logs = db.get_machine_logs(
                machine_id=machine['machine_id'],
                start_date=str(start_date),
                end_date=str(end_date)
            )
            machine_failures = db.get_failures(
                machine_id=machine['machine_id'],
                start_date=str(start_date),
                end_date=str(end_date)
            )
            
            efficiency = calc.calculate_running_time_percentage(machine_logs)
            productivity = calc.calculate_productivity(machine_logs)
            failure_count = len(machine_failures)
            
            # Get latest status
            latest_status = "OFFLINE"
            if not machine_logs.empty:
                latest_status = machine_logs.iloc[0]['status']
            
            machine_metrics.append({
                "Machine ID": machine['machine_id'],
                "Machine Name": machine['machine_name'],
                "Type": machine['machine_type'],
                "Status": config.MACHINE_STATUS.get(latest_status, latest_status),
                "Running Time %": f"{efficiency:.1f}%",
                "Production": productivity['total_production'],
                "Failures": failure_count
            })
        
        metrics_df = pd.DataFrame(machine_metrics)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Charts
        st.subheader("📊 Visualizations")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Running Time % by Machine")
            if not logs_df.empty:
                efficiency_data = []
                for machine_id in machines_df['machine_id']:
                    machine_logs = logs_df[logs_df['machine_id'] == machine_id]
                    efficiency = calc.calculate_running_time_percentage(machine_logs)
                    efficiency_data.append({
                        'Machine': machine_id,
                        'Running Time %': efficiency
                    })
                
                eff_df = pd.DataFrame(efficiency_data)
                fig = px.bar(
                    eff_df,
                    x='Machine',
                    y='Running Time %',
                    color='Running Time %',
                    color_continuous_scale='RdYlGn',
                    text='Running Time %'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No log data available for the selected date range.")
        
        with col2:
            st.markdown("#### Failures by Machine")
            if not failures_df.empty:
                failure_counts = failures_df['machine_id'].value_counts().reset_index()
                failure_counts.columns = ['Machine', 'Failures']
                
                fig = px.bar(
                    failure_counts,
                    x='Machine',
                    y='Failures',
                    color='Failures',
                    color_continuous_scale='Reds',
                    text='Failures'
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No failures recorded in the selected date range!")
        
        # Status distribution
        if not logs_df.empty:
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Overall Status Distribution")
                status_dist = calc.get_status_distribution(logs_df)
                if status_dist:
                    status_df = pd.DataFrame(list(status_dist.items()), 
                                           columns=['Status', 'Percentage'])
                    status_df['Display'] = status_df['Status'].map(config.MACHINE_STATUS)
                    
                    fig = px.pie(
                        status_df,
                        values='Percentage',
                        names='Display',
                        title='Time Distribution by Status',
                        hole=0.4
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Production Over Time")
                production_df = logs_df[logs_df['production_count'] > 0].copy()
                if not production_df.empty:
                    production_df['timestamp'] = pd.to_datetime(production_df['timestamp'])
                    production_df['date'] = production_df['timestamp'].dt.date
                    daily_production = production_df.groupby('date')['production_count'].sum().reset_index()
                    
                    fig = px.line(
                        daily_production,
                        x='date',
                        y='production_count',
                        title='Daily Production Output',
                        markers=True
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No production data available.")

elif page == "🤖 Machine Details":
    st.title("🤖 Machine Details")
    
    machines_df = db.get_all_machines()
    
    if machines_df.empty:
        st.warning("⚠️ No machines found. Please add machines first!")
    else:
        selected_machine = st.selectbox(
            "Select Machine",
            machines_df['machine_id'].tolist(),
            format_func=lambda x: f"{x} - {machines_df[machines_df['machine_id']==x]['machine_name'].values[0]}"
        )
        
        if selected_machine:
            machine_info = machines_df[machines_df['machine_id'] == selected_machine].iloc[0]
            
            # Machine info
            st.subheader("ℹ️ Machine Information")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"**ID:** {machine_info['machine_id']}")
            with col2:
                st.info(f"**Type:** {machine_info['machine_type']}")
            with col3:
                st.info(f"**Location:** {machine_info['location']}")
            with col4:
                st.info(f"**Added:** {machine_info['created_at'][:10]}")
            
            st.markdown("---")
            
            # Get logs and failures
            logs_df = db.get_machine_logs(
                machine_id=selected_machine,
                start_date=str(start_date),
                end_date=str(end_date)
            )
            failures_df = db.get_failures(
                machine_id=selected_machine,
                start_date=str(start_date),
                end_date=str(end_date)
            )
            
            # Metrics
            st.subheader("📊 Performance Metrics")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            efficiency = calc.calculate_running_time_percentage(logs_df)
            productivity = calc.calculate_productivity(logs_df)
            failure_rate = calc.calculate_daily_failure_rate(failures_df)
            
            with col1:
                st.metric("⚡ Running Time %", f"{efficiency:.1f}%")
            with col2:
                st.metric("📦 Total Production", productivity['total_production'])
            with col3:
                st.metric("📈 Production/Hour", f"{productivity['production_per_hour']:.1f}")
            with col4:
                st.metric("⚠️ Total Failures", failure_rate['total_failures'])
            with col5:
                runtime_hours = productivity['total_runtime_hours']
                st.metric("⏱️ Runtime (hours)", f"{runtime_hours:.1f}")
            
            # Additional metrics
            if not logs_df.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    idle_pct = calc.calculate_idle_time_percentage(logs_df)
                    st.metric("💤 Idle Time %", f"{idle_pct:.1f}%")
                
                with col2:
                    downtime_pct = calc.calculate_downtime_percentage(logs_df)
                    st.metric("🔴 Downtime %", f"{downtime_pct:.1f}%")
                
                with col3:
                    if not failures_df.empty and runtime_hours > 0:
                        mtbf = calc.calculate_mtbf(failures_df, runtime_hours)
                        st.metric("🔧 MTBF (hours)", f"{mtbf:.1f}")
                    else:
                        st.metric("🔧 MTBF (hours)", "N/A")
            
            st.markdown("---")
            
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["📋 Recent Logs", "⚠️ Failures", "📊 Charts"])
            
            with tab1:
                st.subheader("Recent Activity Logs")
                if not logs_df.empty:
                    display_logs = logs_df[['timestamp', 'status', 'duration_minutes', 'production_count', 'notes']].head(50)
                    display_logs['status'] = display_logs['status'].map(config.MACHINE_STATUS)
                    display_logs['duration_minutes'] = display_logs['duration_minutes'].round(2)
                    st.dataframe(display_logs, use_container_width=True, hide_index=True)
                    
                    # Download button
                    csv = logs_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Full Logs as CSV",
                        data=csv,
                        file_name=f"{selected_machine}_logs_{start_date}_to_{end_date}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No logs found for selected date range.")
            
            with tab2:
                st.subheader("Failure History")
                if not failures_df.empty:
                    display_failures = failures_df[['timestamp', 'failure_type', 'downtime_minutes', 'resolution']].head(50)
                    display_failures['downtime_minutes'] = display_failures['downtime_minutes'].round(2)
                    st.dataframe(display_failures, use_container_width=True, hide_index=True)
                    
                    # Failure analysis
                    st.markdown("#### Failure Analysis")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        failure_types = failures_df['failure_type'].value_counts().reset_index()
                        failure_types.columns = ['Failure Type', 'Count']
                        fig = px.bar(failure_types, x='Failure Type', y='Count', 
                                   title='Failures by Type')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        mttr = calc.calculate_mttr(failures_df)
                        avg_downtime = failures_df['downtime_minutes'].mean()
                        total_downtime = failures_df['downtime_minutes'].sum()
                        
                        st.metric("⏱️ MTTR (hours)", f"{mttr:.2f}")
                        st.metric("📊 Avg Downtime (min)", f"{avg_downtime:.1f}")
                        st.metric("🔴 Total Downtime (hours)", f"{total_downtime/60:.1f}")
                else:
                    st.success("✅ No failures recorded for selected date range!")
            
            with tab3:
                if not logs_df.empty:
                    # Status distribution pie chart
                    st.markdown("#### Status Distribution")
                    status_dist = calc.get_status_distribution(logs_df)
                    if status_dist:
                        status_df = pd.DataFrame(list(status_dist.items()), 
                                               columns=['Status', 'Percentage'])
                        status_df['Display'] = status_df['Status'].map(config.MACHINE_STATUS)
                        
                        fig = px.pie(status_df, values='Percentage', names='Display',
                                   title='Time Distribution by Status', hole=0.4)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Timeline
                    st.markdown("#### Activity Timeline")
                    logs_df_copy = logs_df.copy()
                    logs_df_copy['timestamp'] = pd.to_datetime(logs_df_copy['timestamp'])
                    logs_df_copy['date'] = logs_df_copy['timestamp'].dt.date
                    logs_df_copy['display_status'] = logs_df_copy['status'].map(config.MACHINE_STATUS)
                    
                    daily_status = logs_df_copy.groupby(['date', 'status'])['duration_minutes'].sum().reset_index()
                    daily_status['display_status'] = daily_status['status'].map(config.MACHINE_STATUS)
                    
                    fig = px.bar(daily_status, x='date', y='duration_minutes', 
                               color='display_status', title='Daily Activity by Status',
                               labels={'duration_minutes': 'Duration (minutes)'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available for charts.")

elif page == "📝 Add Log":
    st.title("📝 Add Machine Log")
    
    machines_df = db.get_all_machines()
    
    if machines_df.empty:
        st.warning("⚠️ No machines found. Please add machines first!")
    else:
        tab1, tab2 = st.tabs(["📊 Status Log", "⚠️ Failure Log"])
        
        with tab1:
            st.subheader("Log Machine Status")
            with st.form("status_log_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    machine_id = st.selectbox(
                        "Machine*",
                        machines_df['machine_id'].tolist(),
                        format_func=lambda x: f"{x} - {machines_df[machines_df['machine_id']==x]['machine_name'].values[0]}"
                    )
                    status = st.selectbox(
                        "Status*",
                        list(config.MACHINE_STATUS.keys()),
                        format_func=lambda x: config.MACHINE_STATUS[x]
                    )
                
                with col2:
                    duration = st.number_input(
                        "Duration (minutes)*",
                        min_value=0.0,
                        value=60.0,
                        step=1.0
                    )
                    production_count = st.number_input(
                        "Production Count",
                        min_value=0,
                        value=0,
                        step=1,
                        help="Number of units produced (leave 0 for non-production statuses)"
                    )
                
                notes = st.text_area("Notes (optional)", placeholder="Additional information...")
                
                submitted = st.form_submit_button("✅ Add Log", use_container_width=True)
                if submitted:
                    try:
                        db.log_machine_status(machine_id, status, duration, production_count, notes)
                        st.success(f"✅ Log added successfully for {machine_id}!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error adding log: {e}")
        
        with tab2:
            st.subheader("Log Machine Failure")
            with st.form("failure_log_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    machine_id = st.selectbox(
                        "Machine *",
                        machines_df['machine_id'].tolist(),
                        format_func=lambda x: f"{x} - {machines_df[machines_df['machine_id']==x]['machine_name'].values[0]}"
                    )
                    failure_type = st.text_input(
                        "Failure Type*",
                        placeholder="e.g., Mechanical Failure, Software Error"
                    )
                
                with col2:
                    downtime = st.number_input(
                        "Downtime (minutes)*",
                        min_value=0.0,
                        value=30.0,
                        step=1.0
                    )
                
                resolution = st.text_area(
                    "Resolution/Notes",
                    placeholder="Describe the resolution or actions taken..."
                )
                
                submitted = st.form_submit_button("⚠️ Log Failure", use_container_width=True)
                if submitted:
                    if failure_type:
                        try:
                            db.log_failure(machine_id, failure_type, downtime, resolution)
                            st.success(f"✅ Failure logged successfully for {machine_id}!")
                        except Exception as e:
                            st.error(f"❌ Error logging failure: {e}")
                    else:
                        st.error("❌ Please specify the failure type!")

elif page == "➕ Add Machine":
    st.title("➕ Add New Machine")
    
    with st.form("add_machine_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            machine_id = st.text_input(
                "Machine ID*",
                placeholder="e.g., M001",
                help="Unique identifier for the machine"
            )
            machine_name = st.text_input(
                "Machine Name*",
                placeholder="e.g., CNC Machine 1"
            )
        
        with col2:
            machine_type = st.selectbox(
                "Machine Type*",
                ["CNC", "Lathe", "Mill", "Press", "Assembly", "Packaging", "Welding", "Cutting", "Other"]
            )
            location = st.text_input(
                "Location",
                placeholder="e.g., Floor A, Section 2"
            )
        
        st.markdown("---")
        submitted = st.form_submit_button("➕ Add Machine", use_container_width=True)
        
        if submitted:
            if machine_id and machine_name:
                try:
                    db.add_machine(machine_id, machine_name, machine_type, location)
                    st.success(f"✅ Machine **{machine_id}** added successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error adding machine: {e}")
            else:
                st.error("❌ Please fill in all required fields (Machine ID and Name)!")
    
    st.markdown("---")
    st.subheader("📋 Existing Machines")
    machines_df = db.get_all_machines()
    if not machines_df.empty:
        st.dataframe(machines_df, use_container_width=True, hide_index=True)
    else:
        st.info("No machines in the database yet.")

elif page == "📈 Analytics":
    st.title("📈 Advanced Analytics")
    
    machines_df = db.get_all_machines()
    
    if machines_df.empty:
        st.warning("⚠️ No machines found. Please add machines first!")
    else:
        logs_df = db.get_machine_logs(start_date=str(start_date), end_date=str(end_date))
        failures_df = db.get_failures(start_date=str(start_date), end_date=str(end_date))
        
        if not logs_df.empty:
            # Production trends
            st.subheader("📦 Production Analysis")
            production_df = logs_df[logs_df['production_count'] > 0].copy()
            
            if not production_df.empty:
                production_df['timestamp'] = pd.to_datetime(production_df['timestamp'])
                production_df['date'] = production_df['timestamp'].dt.date
                
                col1, col2 = st.columns(2)
                
                with col1:
                    daily_production = production_df.groupby('date')['production_count'].sum().reset_index()
                    fig = px.line(
                        daily_production,
                        x='date',
                        y='production_count',
                        title='Daily Production Output',
                        markers=True
                    )
                    fig.update_traces(line_color='#2ecc71')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    machine_production = production_df.groupby('machine_id')['production_count'].sum().reset_index()
                    machine_production.columns = ['Machine', 'Production']
                    fig = px.bar(
                        machine_production,
                        x='Machine',
                        y='Production',
                        title='Total Production by Machine',
                        color='Production',
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Efficiency comparison
            st.subheader("⚡ Efficiency Comparison")
            
            efficiency_data = []
            for _, machine in machines_df.iterrows():
                machine_logs = logs_df[logs_df['machine_id'] == machine['machine_id']]
                
                running_pct = calc.calculate_running_time_percentage(machine_logs)
                idle_pct = calc.calculate_idle_time_percentage(machine_logs)
                downtime_pct = calc.calculate_downtime_percentage(machine_logs)
                
                efficiency_data.append({
                    'Machine': machine['machine_id'],
                    'Running': running_pct,
                    'Idle': idle_pct,
                    'Downtime': downtime_pct
                })
            
            eff_comparison = pd.DataFrame(efficiency_data)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Running', x=eff_comparison['Machine'], 
                                y=eff_comparison['Running'], marker_color='green'))
            fig.add_trace(go.Bar(name='Idle', x=eff_comparison['Machine'], 
                                y=eff_comparison['Idle'], marker_color='yellow'))
            fig.add_trace(go.Bar(name='Downtime', x=eff_comparison['Machine'], 
                                y=eff_comparison['Downtime'], marker_color='red'))
            
            fig.update_layout(barmode='stack', title='Time Distribution by Machine (%)',
                            yaxis_title='Percentage', height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Failure analysis
            if not failures_df.empty:
                st.subheader("⚠️ Failure Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    failures_df['timestamp'] = pd.to_datetime(failures_df['timestamp'])
                    failures_df['date'] = failures_df['timestamp'].dt.date
                    daily_failures = failures_df.groupby('date').size().reset_index(name='count')
                    
                    fig = px.line(
                        daily_failures,
                        x='date',
                        y='count',
                        title='Daily Failure Trend',
                        markers=True
                    )
                    fig.update_traces(line_color='#e74c3c')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    failure_by_type = failures_df['failure_type'].value_counts().head(10).reset_index()
                    failure_by_type.columns = ['Failure Type', 'Count']
                    
                    fig = px.bar(
                        failure_by_type,
                        y='Failure Type',
                        x='Count',
                        orientation='h',
                        title='Top 10 Failure Types',
                        color='Count',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Downtime analysis
                st.markdown("#### 🔴 Downtime Analysis")
                downtime_by_machine = failures_df.groupby('machine_id')['downtime_minutes'].sum().reset_index()
                downtime_by_machine['downtime_hours'] = downtime_by_machine['downtime_minutes'] / 60
                downtime_by_machine.columns = ['Machine', 'Minutes', 'Hours']
                
                fig = px.bar(
                    downtime_by_machine,
                    x='Machine',
                    y='Hours',
                    title='Total Downtime by Machine (Hours)',
                    color='Hours',
                    color_continuous_scale='Reds',
                    text='Hours'
                )
                fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("📊 No data available for the selected date range.")

elif page == "🎲 Generate Sample Data":
    st.title("🎲 Generate Sample Data")
    
    st.markdown("""
    This utility helps you quickly populate the database with realistic sample data for testing purposes.
    """)
    
    st.warning("⚠️ **Warning:** Generating sample data will add new machines, logs, and failures to your database.")
    
    with st.form("generate_data_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            num_machines = st.number_input(
                "Number of Machines",
                min_value=1,
                max_value=20,
                value=5,
                step=1
            )
        
        with col2:
            num_days = st.number_input(
                "Days of History",
                min_value=1,
                max_value=90,
                value=14,
                step=1
            )
        
        submitted = st.form_submit_button("🎲 Generate Sample Data", use_container_width=True)
        
        if submitted:
            with st.spinner("Generating sample data..."):
                try:
                    generator = DataGenerator(db)
                    generator.generate_complete_dataset(
                        num_machines=num_machines,
                        days=num_days
                    )
                    st.success("✅ Sample data generated successfully!")
                    st.balloons()
                    st.info("💡 Go to the Dashboard to view the generated data.")
                except Exception as e:
                    st.error(f"❌ Error generating data: {e}")
    
    st.markdown("---")
    st.subheader("📊 Current Database Status")
    
    machines_df = db.get_all_machines()
    logs_df = db.get_machine_logs()
    failures_df = db.get_failures()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🤖 Total Machines", len(machines_df))
    with col2:
        st.metric("📝 Total Logs", len(logs_df))
    with col3:
        st.metric("⚠️ Total Failures", len(failures_df))

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Machine Efficiency Tracker v1.0 | Built with Streamlit ⚙️"
    "</div>",
    unsafe_allow_html=True
)


