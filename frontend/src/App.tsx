import React, { useState } from 'react';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import { CloudUploadOutlined } from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#ff80ab', // プライマリカラーをピンクに変更
    },
    secondary: {
      main: '#5c6bc0', // セカンダリカラーを紫に変更
    },
  },
  typography: {
    fontFamily: "'Kosugi Maru', sans-serif", // フォントを'Kosugi Maru'に変更
  },
});

function App() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      setLoading(true);

      try {
        const response = await fetch('http://localhost:8000/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          setImageUrl(url);
        } else {
          throw new Error('Failed to upload file');
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          backgroundImage: 'url("https://example.com/background-image.jpg")', // 背景画像を指定
          backgroundSize: 'cover',
          minHeight: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Box sx={{ p: 2, backgroundColor: 'rgba(0, 0, 0, 0.8)', borderRadius: '10px', maxWidth: '600px', width: '100%' }}>
          <Grid container spacing={2} justifyContent="center">
            <Grid item xs={12} sm={6}>
              <label htmlFor="upload-input">
                <input type="file" accept="video/*" onChange={handleFileChange} style={{ display: 'none' }} id="upload-input" />
                <Button
                  variant="contained"
                  component="span"
                  startIcon={<CloudUploadOutlined />}
                  sx={{
                    borderRadius: '30px', // ボタンの角丸を変更
                    backgroundColor: theme.palette.primary.main,
                    color: '#fff',
                    '&:hover': {
                      backgroundColor: theme.palette.secondary.main,
                    },
                    whiteSpace: 'normal', // ボタン内のテキストの折り返しを有効にする
                    overflow: 'hidden', // ボタン内の要素がはみ出た場合に非表示にする
                    padding: '10px', // ボタン内の余白を追加
                  }}
                >
                  <Typography variant="body1" sx={{ maxWidth: '100%', overflowWrap: 'break-word' }}>
                    {imageUrl ? 'Replace File' : 'Upload File'}
                  </Typography>
                </Button>
              </label>
            </Grid>
            <Grid item xs={12} sm={6} sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <Box
                sx={{
                  boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.3)', // 影を追加
                  borderRadius: '10px', // 画像の角丸を変更
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
                        objectFit: 'cover', // 画像のアスペクト比を維持
                      }}
                    />
                    <Box
                      sx={{
                        backgroundColor: theme.palette.primary.main,
                        color: '#fff',
                        padding: '8px',
                        textAlign: 'center',
                      }}
                    >
                      <Typography variant="body1" sx={{ overflowWrap: 'break-word' }}>
                        Processed Image
                      </Typography>
                    </Box>
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
