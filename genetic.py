import tkinter as tk
from tkinter import messagebox
import random
from music21 import *

NOTES = {
    'Joy': ['C5', 'E5', 'G5', 'B5', 'D6', 'C6'],
    'Sadness': ['A3', 'C4', 'E4', 'G4', 'B3'],
    'Anger': ['D4', 'F4', 'A4', 'B4', 'C5'],
    'Calm': ['F4', 'A4', 'C5', 'E5', 'G4']
}
NOTE_DURATIONS = {
    'Joy': [0.25, 0.5, 0.75, 1.0],
    'Sadness': [1.0, 1.5, 2.0, 3.0],
    'Anger': [0.25, 0.5, 0.75, 1.0],
    'Calm': [1.0, 1.5, 2.0, 3.0]
}
INSTRUMENTS = {
    'Piano': instrument.Piano(),
    'Guitar': instrument.Guitar(),
    'Flute': instrument.Flute(),
    'Violin': instrument.Violin()
}
CHORDS = {
    'Joy': [['C5', 'E5', 'G5'], ['D5', 'G5', 'B5']],
    'Sadness': [['A3', 'C4', 'E4'], ['G3', 'B3', 'D4']],
    'Anger': [['D4', 'F4', 'A4'], ['C4', 'E4', 'G4']],
    'Calm': [['F4', 'A4', 'C5'], ['E4', 'G4', 'B4']]
}

NUM_BARS = 8
POPULATION_SIZE = 10
MUTATION_RATE = 0.1
NUM_GENERATIONS = 20

def generate_measure(emotion, instrument_name):
    selected_instrument = INSTRUMENTS[instrument_name]
    measure = stream.Measure()
    measure.append(selected_instrument)
    notes_pool = NOTES[emotion]
    chords_pool = CHORDS[emotion]
    durations_pool = NOTE_DURATIONS[emotion]
    duration = 0

    while duration < 4.0:
        if random.random() < 0.3:
            n = chord.Chord(random.choice(chords_pool))
        else:
            n = note.Note(random.choice(notes_pool))
        n.quarterLength = random.choice(durations_pool)
        if duration + n.quarterLength <= 4.0:
            measure.append(n)
            duration += n.quarterLength

    return measure

def generate_chromosome(emotion, instrument_name):
    return [generate_measure(emotion, instrument_name) for _ in range(NUM_BARS)]

def fitness_function(chromosome):
    unique_notes = set()
    for measure in chromosome:
        for element in measure.notes:
            if isinstance(element, note.Note):
                unique_notes.add(element.name)
            elif isinstance(element, chord.Chord):
                unique_notes.update([n.name for n in element.notes])
    return len(unique_notes)

def crossover(parent1, parent2):
    split_point = random.randint(1, NUM_BARS - 1)
    return parent1[:split_point] + parent2[split_point:]

def mutate(chromosome, emotion, instrument_name):
    for i in range(len(chromosome)):
        if random.random() < MUTATION_RATE:
            chromosome[i] = generate_measure(emotion, instrument_name)
    return chromosome

def genetic_algorithm(emotion, instrument_name):
    population = [generate_chromosome(emotion, instrument_name) for _ in range(POPULATION_SIZE)]

    for generation in range(NUM_GENERATIONS):
        fitness_scores = [(chromosome, fitness_function(chromosome)) for chromosome in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)

        top_individuals = [x[0] for x in fitness_scores[:POPULATION_SIZE // 2]]
        next_generation = top_individuals.copy()

        while len(next_generation) < POPULATION_SIZE:
            parent1, parent2 = random.sample(top_individuals, 2)
            child = crossover(parent1, parent2)
            child = mutate(child, emotion, instrument_name)
            next_generation.append(child)

        population = next_generation
        print(f"Generation {generation + 1}: Best fitness = {fitness_scores[0][1]}")

    return max(population, key=fitness_function)

def chromosome_to_score(chromosome):
    score = stream.Score()
    for measure in chromosome:
        score.append(measure)
    return score

def transcribe_chromosome(chromosome):
    with open('melody_transcription.txt', 'w') as file:
        for measure in chromosome:
            for element in measure.notes:
                if isinstance(element, note.Note):
                    file.write(f"Note: {element.name} Duration: {element.quarterLength}\n")
                elif isinstance(element, chord.Chord):
                    file.write(f"Chord: {'-'.join(n.name for n in element.notes)} Duration: {element.quarterLength}\n")

class MusicApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Emotional Melody Generator')
        self.root.geometry('400x400')

        tk.Label(root, text="🎵 Select an Emotion:", font=("Helvetica", 14)).grid(row=0, column=0, pady=10)
        self.emotion_var = tk.StringVar(value='Joy')
        tk.OptionMenu(root, self.emotion_var, *NOTES.keys()).grid(row=1, column=0, pady=5)

        tk.Label(root, text="🎸 Select an Instrument:", font=("Helvetica", 14)).grid(row=2, column=0, pady=10)
        self.instrument_var = tk.StringVar(value='Piano')
        tk.OptionMenu(root, self.instrument_var, *INSTRUMENTS.keys()).grid(row=3, column=0, pady=5)

        tk.Button(root, text="🎼 Generate Melody", command=self.play_melody, bg="lightblue", font=("Helvetica", 13)).grid(row=4, column=0, pady=20)

    def play_melody(self):
        try:
            emotion = self.emotion_var.get()
            instrument_name = self.instrument_var.get()
            best_music = genetic_algorithm(emotion, instrument_name)
            score = chromosome_to_score(best_music)
            transcribe_chromosome(best_music)
            score.show('text')
            sp = midi.realtime.StreamPlayer(score)
            sp.play()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicApp(root)
    root.mainloop()
