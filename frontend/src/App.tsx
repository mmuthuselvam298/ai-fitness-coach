import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { ExerciseSelectPage } from './pages/ExerciseSelectPage';
import { WorkoutCameraPage } from './pages/WorkoutCameraPage';
import { WorkoutSummaryPage } from './pages/WorkoutSummaryPage';
import { HistoryPage } from './pages/HistoryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { DemoPage } from './pages/DemoPage';
import { AboutPage } from './pages/AboutPage';
import { ExerciseMetadata, WorkoutSummary } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<string>('landing');
  const [exercises, setExercises] = useState<ExerciseMetadata[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<ExerciseMetadata | null>(null);
  const [workoutTargetReps, setWorkoutTargetReps] = useState<number>(12);
  const [workoutMode, setWorkoutMode] = useState<'webcam' | 'demo' | 'upload'>('webcam');
  const [activeSummary, setActiveSummary] = useState<WorkoutSummary | null>(null);

  useEffect(() => {
    api.getExercises()
      .then((data) => {
        setExercises(data);
        if (data.length > 0) {
          setSelectedExercise(data[0]);
        }
      })
      .catch((err) => {
        console.error('Failed to load exercises catalog:', err);
      });
  }, []);

  const handleStartWorkoutFromLanding = () => {
    setCurrentView('exercises');
  };

  const handleTryDemoFromLanding = () => {
    setCurrentView('demo');
  };

  const handleSelectExercise = (
    exerciseId: string,
    targetReps: number,
    mode: 'webcam' | 'demo' | 'upload'
  ) => {
    const ex = exercises.find((e) => e.id === exerciseId) || exercises[0];
    setSelectedExercise(ex);
    setWorkoutTargetReps(targetReps);
    setWorkoutMode(mode);
    setCurrentView('workout');
  };

  const handleLaunchDemoWorkout = (exerciseId: string) => {
    const ex = exercises.find((e) => e.id === exerciseId) || exercises[0];
    setSelectedExercise(ex);
    setWorkoutTargetReps(3);
    setWorkoutMode('demo');
    setCurrentView('workout');
  };

  const handleFinishWorkout = (summary: WorkoutSummary) => {
    setActiveSummary(summary);
    setCurrentView('summary');
  };

  const handleViewWorkoutDetail = (summary: WorkoutSummary) => {
    setActiveSummary(summary);
    setCurrentView('summary');
  };

  return (
    <div className="app-container">
      <Navbar currentView={currentView} onNavigate={(view) => setCurrentView(view)} />

      <main className="content-wrapper">
        {currentView === 'landing' && (
          <LandingPage
            onStartWorkout={handleStartWorkoutFromLanding}
            onTryDemo={handleTryDemoFromLanding}
            onNavigateAbout={() => setCurrentView('about')}
            exercises={exercises}
          />
        )}

        {currentView === 'exercises' && (
          <ExerciseSelectPage
            exercises={exercises}
            onSelectExercise={handleSelectExercise}
            onBack={() => setCurrentView('landing')}
          />
        )}

        {currentView === 'workout' && selectedExercise && (
          <WorkoutCameraPage
            exercise={selectedExercise}
            targetReps={workoutTargetReps}
            initialMode={workoutMode}
            onFinishWorkout={handleFinishWorkout}
            onCancel={() => setCurrentView('exercises')}
          />
        )}

        {currentView === 'summary' && activeSummary && (
          <WorkoutSummaryPage
            summary={activeSummary}
            onDone={() => setCurrentView('history')}
            onWorkoutAgain={() => setCurrentView('exercises')}
          />
        )}

        {currentView === 'history' && (
          <HistoryPage
            onStartNewWorkout={() => setCurrentView('exercises')}
            onViewWorkoutDetail={handleViewWorkoutDetail}
          />
        )}

        {currentView === 'analytics' && <AnalyticsPage />}

        {currentView === 'demo' && (
          <DemoPage onLaunchDemoWorkout={handleLaunchDemoWorkout} />
        )}

        {currentView === 'about' && (
          <AboutPage onStartWorkout={() => setCurrentView('exercises')} />
        )}
      </main>

      <Footer />
    </div>
  );
};

export default App;
