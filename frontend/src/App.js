import React, { useState, useEffect } from 'react';
import {
  Container,
  Button,
  Box,
  Typography,
  Paper,
  Chip,
  Stack,
  CircularProgress,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardActions,
  Grid,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
} from '@mui/material';
import axios from 'axios';

const DIETARY_OPTIONS = [
  'No Beef',
  'No Pork',
  'No Dairy',
  'No Nuts',
  'No Shellfish',
  'Vegetarian',
  'Vegan',
  'Gluten-Free',
  'Halal',
  'Kosher',
];

const MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner'];

function App() {
  const [selectedRestrictions, setSelectedRestrictions] = useState([]);
  const [customRestriction, setCustomRestriction] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [selectedMealType, setSelectedMealType] = useState(0);
  const [days, setDays] = useState([]);
  const [selectedDay, setSelectedDay] = useState('');
  const [selectedMealTime, setSelectedMealTime] = useState('');
  const [loadingDays, setLoadingDays] = useState(true);
  const [maxCalories, setMaxCalories] = useState('');

  useEffect(() => {
    // Fetch available days from the backend
    const fetchDays = async () => {
      try {
        setLoadingDays(true);
        setError('');
        const response = await axios.get('http://localhost:8000/available-days');
        if (response.data && response.data.days) {
          setDays(response.data.days);
          if (response.data.days.length > 0) {
            setSelectedDay(response.data.days[0]);
          }
        } else {
          setError('Invalid response format from server');
        }
      } catch (err) {
        console.error('Error fetching days:', err);
        setError('Failed to load available days. Please try again later.');
      } finally {
        setLoadingDays(false);
      }
    };
    fetchDays();
  }, []);

  const handleRestrictionToggle = (restriction) => {
    setSelectedRestrictions((prev) =>
      prev.includes(restriction)
        ? prev.filter((r) => r !== restriction)
        : [...prev, restriction]
    );
  };

  const handleCustomRestrictionAdd = () => {
    if (customRestriction.trim()) {
      setSelectedRestrictions((prev) => [...prev, customRestriction.trim()]);
      setCustomRestriction('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedDay || !selectedMealTime) {
      setError('Please select both day and meal time');
      return;
    }
    
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('http://localhost:8000/analyze-menu', {
        dietary_restrictions: selectedRestrictions,
        day: selectedDay,
        meal_time: selectedMealTime,
        max_calories: maxCalories ? parseInt(maxCalories) : null,
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleMealTypeChange = (event, newValue) => {
    setSelectedMealType(newValue);
  };

  const renderMenuItem = (item) => (
    <Card key={item.name} sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6">
          {item.name}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        UC Davis Tercero Dining Commons Menu Analyzer
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <form onSubmit={handleSubmit}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Select Your Dietary Restrictions
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" gap={1} sx={{ mb: 2 }}>
            {DIETARY_OPTIONS.map((option) => (
              <Chip
                key={option}
                label={option}
                onClick={() => handleRestrictionToggle(option)}
                color={selectedRestrictions.includes(option) ? 'primary' : 'default'}
              />
            ))}
          </Stack>

          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              fullWidth
              label="Add Custom Dietary Restriction"
              value={customRestriction}
              onChange={(e) => setCustomRestriction(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleCustomRestrictionAdd();
                }
              }}
            />
            <Button
              variant="outlined"
              onClick={handleCustomRestrictionAdd}
              disabled={!customRestriction.trim()}
            >
              Add
            </Button>
          </Box>

          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
            {selectedRestrictions.map((restriction) => (
              <Chip
                key={restriction}
                label={restriction}
                onDelete={() => handleRestrictionToggle(restriction)}
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>

          <Box sx={{ mt: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Select Day</InputLabel>
              <Select
                value={selectedDay}
                label="Select Day"
                onChange={(e) => setSelectedDay(e.target.value)}
                disabled={loadingDays}
              >
                {loadingDays ? (
                  <MenuItem disabled>
                    <CircularProgress size={20} />
                  </MenuItem>
                ) : days.length === 0 ? (
                  <MenuItem disabled>No days available</MenuItem>
                ) : (
                  days.map((day) => (
                    <MenuItem key={day} value={day}>
                      {day}
                    </MenuItem>
                  ))
                )}
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Select Meal Time</InputLabel>
              <Select
                value={selectedMealTime}
                label="Select Meal Time"
                onChange={(e) => setSelectedMealTime(e.target.value)}
              >
                {MEAL_TYPES.map((mealType) => (
                  <MenuItem key={mealType} value={mealType}>
                    {mealType}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Max Calories (Optional)"
              type="number"
              value={maxCalories}
              onChange={(e) => setMaxCalories(e.target.value)}
              sx={{ minWidth: 200 }}
              inputProps={{ min: 0 }}
            />
          </Box>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              type="submit"
              disabled={loading || selectedRestrictions.length === 0 || !selectedDay || !selectedMealTime}
              sx={{ minWidth: 200 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Analyze Menu'}
            </Button>
          </Box>
        </form>
      </Paper>

      {error && (
        <Paper elevation={3} sx={{ p: 3, mb: 3, bgcolor: '#ffebee' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}

      {result && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Menu Analysis for {result.date} {selectedMealTime}
          </Typography>
          {result.total_calories > 0 && (
            <Typography variant="subtitle1" color="primary" gutterBottom>
              Total Calories: {result.total_calories}
              {maxCalories && result.total_calories > parseInt(maxCalories) && (
                <Typography component="span" color="error" sx={{ ml: 1 }}>
                  (Exceeds your limit of {maxCalories} calories)
                </Typography>
              )}
            </Typography>
          )}
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6" gutterBottom>
            Safe Menu Items:
          </Typography>
          {result.menu_items.map((item) => renderMenuItem(item))}
        </Paper>
      )}
    </Container>
  );
}

export default App;
