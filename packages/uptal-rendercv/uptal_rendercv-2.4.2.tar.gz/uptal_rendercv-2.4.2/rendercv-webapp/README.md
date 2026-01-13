# RenderCV React Web Application

A modern React-based web application for creating professional CVs/resumes using the RenderCV engine. Features a intuitive form builder on the left and live PDF preview on the right.

## 🚀 Features

- **Modern Tech Stack**: React 18 with TypeScript, Material-UI components
- **Live PDF Preview**: See changes in real-time as you type
- **Smart Form Builder**: Dynamic sections with different entry types
- **Multiple Themes**: 5 built-in professional themes
- **Import/Export**: Support for YAML, JSON, and Markdown formats
- **Auto-save**: Automatically saves to browser localStorage
- **Responsive Design**: Works on desktop and tablet devices
- **Drag & Drop**: Reorder sections easily (coming soon)

## 📋 Prerequisites

- Docker and Docker Compose
- OR Node.js 20+ and Python 3.10+

## 🛠️ Installation & Setup

### Option 1: Using Docker (Recommended)

1. Clone the repository and navigate to the webapp:
```bash
cd rendercv-webapp
``` 

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api

### Option 2: Local Development

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

#### Frontend Setup
```bash
# From the root directory (e.g., /d/work/UpTal/cv-enhancer)
cd rendercv-webapp/frontend
yarn install  # or npm install
yarn run dev  # or npm run dev
```

**Quick Start from Root:**
```bash
# Navigate to frontend directory and run dev server
cd rendercv-webapp/frontend && yarn run dev
```

## 🏗️ Project Structure

```
rendercv-webapp/
├── backend/                 # Flask API server
│   ├── app.py              # Main API application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── FormBuilder/
│   │   │   ├── PdfViewer/
│   │   │   └── Layout/
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx       # Main app component
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## 💻 Usage

### Getting Started

1. **Start Fresh**: Click your name to begin building your CV
2. **Load Sample**: Click "Load Sample" in the header to see an example
3. **Import Existing**: Click "Import" to load a YAML file

### Building Your CV

#### Personal Information
- Enter basic details (name, email, phone, etc.)
- Add social media profiles (LinkedIn, GitHub, etc.)

#### Sections
- Click "Add Section" to create new sections
- Choose from templates:
  - **Experience**: Work history with highlights
  - **Education**: Academic background
  - **Skills**: Bullet-point skills
  - **Projects**: Project descriptions
  - **Publications**: Academic publications

#### Themes
- Select from 5 professional themes
- Customize colors and fonts

### Exporting

- **PDF**: Download the generated PDF
- **YAML**: Export for use with RenderCV CLI
- **JSON**: Export as structured data
- **Markdown**: Export as markdown text

## 🔧 Development

### Backend API Endpoints

- `POST /api/render` - Generate PDF from CV data
- `GET /api/themes` - Get available themes
- `GET /api/sample` - Get sample CV data
- `POST /api/validate` - Validate CV structure
- `POST /api/export/:format` - Export CV
- `POST /api/import` - Import YAML file

### Frontend Components

#### FormBuilder
- `PersonalInfo.tsx` - Personal details form
- `SocialNetworks.tsx` - Social media links
- `SectionManager.tsx` - Manage CV sections
- `SectionEntry.tsx` - Individual section entries
- `ThemeSelector.tsx` - Theme selection

#### PdfViewer
- Real-time PDF rendering
- Download functionality
- Error handling

### State Management

Uses React Context API (`useCV` hook) for global state management with localStorage persistence.

## 🐛 Troubleshooting

### PDF not generating
- Ensure name field is filled
- Check browser console for errors
- Verify backend is running on port 5000

### Docker issues
```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Port conflicts
- Frontend: Change port in `frontend/vite.config.ts`
- Backend: Change port in `backend/app.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project uses the RenderCV engine which is MIT licensed.

## 🔗 Links

- [RenderCV GitHub](https://github.com/rendercv/rendercv)
- [RenderCV Documentation](https://docs.rendercv.com)

## 🙏 Credits

Built on top of the excellent [RenderCV](https://github.com/rendercv/rendercv) project by Sina Atalay.