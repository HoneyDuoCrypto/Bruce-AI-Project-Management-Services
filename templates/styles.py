"""
Shared CSS styles for all Bruce templates
Contains all styling and responsive design from original system
"""

def get_shared_styles():
    """Returns the complete CSS for Bruce UI"""
    return """
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d30 100%);
                color: #ffffff; 
                line-height: 1.6;
                min-height: 100vh;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { 
                background: linear-gradient(135deg, #2b2b2b 0%, #1a1a1a 100%);
                padding: 30px 0; 
                border-bottom: 3px solid {{ theme_color }};
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            }
            .header h1 { 
                color: {{ theme_color }}; 
                text-align: center; 
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                margin-bottom: 10px;
            }
            .domain-badge { 
                text-align: center; 
                color: #888;
                font-size: 14px;
                margin-bottom: 20px;
            }
            .nav { 
                display: flex; 
                justify-content: center; 
                gap: 20px; 
                flex-wrap: wrap;
            }
            .nav a { 
                color: #ffffff; 
                text-decoration: none; 
                padding: 12px 24px;
                background: linear-gradient(135deg, #333 0%, #555 100%);
                border-radius: 8px; 
                transition: all 0.3s ease;
                border: 1px solid transparent;
                font-weight: 500;
            }
            .nav a:hover, .nav a.active { 
                background: linear-gradient(135deg, {{ theme_color }} 0%, {{ theme_color_light }} 100%);
                color: #000; 
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,212,170,0.3);
            }
            .content-section { 
                background: rgba(43, 43, 43, 0.8);
                border-radius: 15px; 
                padding: 25px; 
                margin: 20px 0;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            }
            .section-title { 
                color: {{ theme_color }}; 
                margin-bottom: 20px; 
                font-size: 1.5em;
                border-bottom: 2px solid {{ theme_color }};
                padding-bottom: 10px;
            }
            .btn { 
                padding: 10px 20px; 
                border: none; 
                border-radius: 8px;
                cursor: pointer; 
                font-weight: bold; 
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
                font-size: 14px;
            }
            .btn:hover { 
                transform: translateY(-2px); 
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }
            .btn-primary { background: linear-gradient(135deg, {{ theme_color }} 0%, {{ theme_color_light }} 100%); color: #000; }
            .btn-success { background: linear-gradient(135deg, #00cc00 0%, #009900 100%); color: white; }
            .btn-info { background: linear-gradient(135deg, #0066cc 0%, #004499 100%); color: white; }
            .btn-danger { background: linear-gradient(135deg, #cc0000 0%, #990000 100%); color: white; }
            .btn-warning { background: linear-gradient(135deg, #ff8c00 0%, #ff6b35 100%); color: white; }
            .btn-secondary { background: linear-gradient(135deg, #666 0%, #888 100%); color: white; }
            .task-item { 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                padding: 20px; 
                margin: 15px 0; 
                background: rgba(51, 51, 51, 0.8);
                border-radius: 10px;
                border-left: 4px solid {{ theme_color }};
                transition: all 0.3s ease;
            }
            .task-item:hover {
                background: rgba(51, 51, 51, 1);
                transform: translateX(5px);
            }
            .task-info { flex: 1; }
            .task-title { font-weight: bold; margin-bottom: 8px; font-size: 18px; }
            .task-meta { color: #ccc; font-size: 14px; margin-bottom: 4px; }
            .task-actions { display: flex; gap: 10px; flex-wrap: wrap; }
            .form-group { margin: 20px 0; }
            .form-group label { 
                display: block; 
                margin-bottom: 8px; 
                color: {{ theme_color }}; 
                font-weight: bold;
            }
            .form-group select, .form-group textarea, .form-group input {
                width: 100%; 
                padding: 12px; 
                border: 1px solid #555; 
                border-radius: 8px;
                background: #333; 
                color: #fff;
                font-size: 16px;
                font-family: inherit;
            }
            .form-group select:focus, .form-group textarea:focus, .form-group input:focus {
                outline: none;
                border-color: {{ theme_color }};
                box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.2);
            }
            .form-row { 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 20px; 
            }
            .form-row-thirds { 
                display: grid; 
                grid-template-columns: 1fr 1fr 1fr; 
                gap: 15px; 
            }
            .report-area { 
                background: #1a1a1a; 
                color: #ffffff; 
                padding: 20px; 
                border-radius: 10px;
                font-family: 'Courier New', monospace; 
                white-space: pre-wrap;
                min-height: 300px; 
                margin: 20px 0;
                border: 2px solid {{ theme_color }};
                font-size: 13px;
                line-height: 1.4;
                overflow-y: auto;
                max-height: 600px;
            }
            .generator-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .generator-card {
                background: rgba(30, 30, 30, 0.8);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid rgba(0, 212, 170, 0.3);
                transition: all 0.3s ease;
            }
            .generator-card:hover {
                border-color: {{ theme_color }};
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 212, 170, 0.2);
            }
            .card-title {
                color: {{ theme_color }};
                font-size: 1.3em;
                font-weight: bold;
                margin-bottom: 15px;
                text-align: center;
            }
            .card-description {
                color: #ccc;
                margin-bottom: 20px;
                text-align: center;
            }
            .stats-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin: 20px 0; 
            }
            .stat-box { 
                padding: 20px; 
                border-radius: 15px; 
                text-align: center; 
                color: white; 
                font-weight: bold;
                transition: all 0.3s ease;
                border: 1px solid rgba(255,255,255,0.1);
            }
            .stat-box:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
            .stat-number { font-size: 2.5em; margin-bottom: 10px; }
            .stat-label { font-size: 1em; opacity: 0.9; }
            .stat-pending { background: linear-gradient(135deg, #ff8c00 0%, #ff6b35 100%); }
            .stat-in-progress { background: linear-gradient(135deg, #0066cc 0%, #004499 100%); }
            .stat-completed { background: linear-gradient(135deg, #00cc00 0%, #009900 100%); }
            .stat-blocked { background: linear-gradient(135deg, #cc0000 0%, #990000 100%); }
            .success { color: #00ff00; font-weight: bold; }
            .error { color: #ff6b6b; font-weight: bold; }
            .info { color: #0099ff; font-weight: bold; }
            .time-display { 
                text-align: center; 
                color: #aaa; 
                font-size: 14px; 
                margin: 15px 0; 
            }
            .status-message {
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                font-weight: bold;
            }
            .status-success { background: rgba(0, 204, 0, 0.2); color: #00ff00; border: 1px solid #00cc00; }
            .status-error { background: rgba(204, 0, 0, 0.2); color: #ff6b6b; border: 1px solid #cc0000; }
            .status-info { background: rgba(0, 102, 204, 0.2); color: #0099ff; border: 1px solid #0066cc; }
            .empty-state {
                text-align: center;
                color: #888;
                padding: 60px 20px;
                font-size: 18px;
            }
            .phase-section {
                margin: 30px 0;
                padding: 20px;
                background: rgba(30, 30, 30, 0.5);
                border-radius: 12px;
                border: 1px solid rgba(0, 212, 170, 0.2);
            }
            .phase-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .phase-title {
                font-size: 1.3em;
                color: {{ theme_color }};
                font-weight: bold;
            }
            .phase-progress {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .progress-bar {
                width: 200px;
                height: 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, {{ theme_color }} 0%, {{ theme_color_light }} 100%);
                transition: width 0.3s ease;
            }
            .progress-text {
                font-size: 14px;
                color: #ccc;
            }
            /* Enhanced context modal styles */
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
            }
            .modal-content {
                background-color: #2b2b2b;
                margin: 5% auto;
                padding: 20px;
                border: 2px solid {{ theme_color }};
                border-radius: 10px;
                width: 80%;
                max-width: 800px;
                max-height: 80vh;
                overflow-y: auto;
                color: #fff;
            }
            .close {
                color: {{ theme_color }};
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }
            .close:hover {
                color: {{ theme_color_light }};
            }
            .checkbox-container {
                margin: 15px 0;
                padding: 15px;
                background: rgba(0, 212, 170, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(0, 212, 170, 0.3);
            }
            .checkbox-container label {
                display: flex;
                align-items: center;
                cursor: pointer;
            }
            .checkbox-container input[type="checkbox"] {
                margin-right: 10px;
                width: 20px;
                height: 20px;
                cursor: pointer;
            }
            .related-tasks {
                margin: 20px 0;
                padding: 15px;
                background: rgba(30, 30, 30, 0.8);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .related-task {
                padding: 10px;
                margin: 5px 0;
                background: rgba(51, 51, 51, 0.8);
                border-radius: 5px;
                border-left: 3px solid {{ theme_color }};
            }
            /* Management form styles */
            .management-tabs {
                display: flex;
                margin-bottom: 20px;
                border-bottom: 2px solid #333;
            }
            .tab {
                padding: 15px 25px;
                background: rgba(51, 51, 51, 0.8);
                color: #ccc;
                cursor: pointer;
                border: none;
                border-bottom: 3px solid transparent;
                transition: all 0.3s ease;
            }
            .tab.active {
                background: rgba(0, 212, 170, 0.1);
                color: {{ theme_color }};
                border-bottom-color: {{ theme_color }};
            }
            .tab-content {
                display: none;
                animation: fadeIn 0.3s ease;
            }
            .tab-content.active {
                display: block;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .dynamic-fields {
                background: rgba(30, 30, 30, 0.8);
                border-radius: 8px;
                padding: 20px;
                margin: 15px 0;
                border: 1px solid rgba(0, 212, 170, 0.2);
            }
            .field-row {
                display: flex;
                gap: 10px;
                align-items: center;
                margin: 10px 0;
            }
            .field-row input {
                flex: 1;
                padding: 8px 12px;
                background: #333;
                border: 1px solid #555;
                border-radius: 6px;
                color: #fff;
            }
            .remove-btn {
                background: #cc0000;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            }
            .add-btn {
                background: #00cc00;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 10px;
            }
            .config-info {
                background: rgba(30, 30, 30, 0.6);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid {{ theme_color }};
            }
            @media (max-width: 768px) {
                .task-item { flex-direction: column; align-items: flex-start; }
                .task-actions { margin-top: 15px; width: 100%; }
                .nav { gap: 10px; }
                .nav a { padding: 8px 16px; font-size: 14px; }
                .progress-bar { width: 150px; }
                .generator-grid { grid-template-columns: 1fr; }
                .form-row { grid-template-columns: 1fr; }
                .form-row-thirds { grid-template-columns: 1fr; }
                .management-tabs { flex-wrap: wrap; }
            }
    """