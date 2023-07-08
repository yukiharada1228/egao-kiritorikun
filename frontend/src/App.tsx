import React, { useState } from 'react';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import LinearProgress from '@mui/material/LinearProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import { CloudUploadOutlined, GetAppOutlined } from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#ff80ab',
    },
    secondary: {
      main: '#5c6bc0',
    },
  },
  typography: {
    fontFamily: "'Kosugi Maru', sans-serif",
  },
});

function App() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
  
      setLoading(true);
  
      const xhr = new XMLHttpRequest();
      xhr.open('POST', 'http://localhost:8000/upload', true);
  
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded * 100) / event.total);
          setUploadProgress(progress);
        }
      };
  
      xhr.onload = async () => {
        if (xhr.status === 200) {
          const blob = xhr.response;
          const url = URL.createObjectURL(blob);
          setImageUrl(url);
        } else {
          console.error('Failed to upload file');
        }
  
        setLoading(false);
      };
  
      xhr.onerror = () => {
        console.error('Error occurred while uploading file');
        setLoading(false);
      };
  
      xhr.responseType = 'blob'; // レスポンスの形式をBlobに設定
      xhr.send(formData);
    }
  };

  const handleDownload = () => {
    if (imageUrl) {
      const link = document.createElement('a');
      link.href = imageUrl;
      link.download = 'processed_image.jpg';
      link.target = '_blank';
  
      document.body.appendChild(link);
      link.click();
  
      document.body.removeChild(link);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          backgroundImage: 'url("https://example.com/background-image.jpg")',
          backgroundSize: 'cover',
          minHeight: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Box
          sx={{
            p: 2,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            borderRadius: '10px',
            maxWidth: '800px',
            width: '100%',
          }}
        >
          <Grid container spacing={2} justifyContent="space-around">
            <Grid item xs={12}>
              <label htmlFor="upload-input">
                <input type="file" accept="video/*" onChange={handleFileChange} style={{ display: 'none' }} id="upload-input" />
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<CloudUploadOutlined />}
                  sx={{
                    borderRadius: '30px',
                    backgroundColor: theme.palette.primary.main,
                    color: '#fff',
                    '&:hover': {
                      backgroundColor: theme.palette.secondary.main,
                    },
                    whiteSpace: 'normal',
                    overflow: 'hidden',
                    padding: '10px',
                    width: '100%',
                  }}
                >
                  <Typography variant="body1" sx={{ maxWidth: '100%', overflowWrap: 'break-word' }}>
                    {imageUrl ? 'Replace File' : 'Upload File'}
                  </Typography>
                </Button>
              </label>
              {uploadProgress > 0 && <LinearProgress variant="determinate" value={uploadProgress} />}
            </Grid>
            <Grid item xs={12}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  flexDirection: 'column',
                  boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.3)',
                  borderRadius: '10px',
                  overflow: 'hidden',
                  width: '100%',
                }}
              >
                {loading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '250px', width: '100%' }}>
                    <CircularProgress sx={{ color: theme.palette.secondary.main }} />
                  </Box>
                ) : imageUrl ? (
                  <Box>
                    <img
                      src={imageUrl}
                      alt="Processed Image"
                      style={{
                        width: '100%',
                        objectFit: 'cover',
                      }}
                    />
                    <Button
                      variant="contained"
                      startIcon={<GetAppOutlined />}
                      onClick={handleDownload}
                      sx={{
                        borderRadius: '30px',
                        backgroundColor: theme.palette.secondary.main,
                        color: '#fff',
                        '&:hover': {
                          backgroundColor: theme.palette.primary.main,
                        },
                        whiteSpace: 'normal',
                        overflow: 'hidden',
                        padding: '10px',
                        marginTop: '10px',
                        width: '100%',
                      }}
                    >
                      <Typography variant="body1" sx={{ maxWidth: '100%', overflowWrap: 'break-word' }}>
                        Download File
                      </Typography>
                    </Button>
                  </Box>
                ) : (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '250px' }}>
                    <Typography variant="body1" sx={{ color: theme.palette.primary.main }}>
                      No file uploaded
                    </Typography>
                  </Box>
                )}
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;