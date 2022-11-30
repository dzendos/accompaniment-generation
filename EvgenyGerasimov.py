import music21
import random
import mido
from dataclasses import dataclass

""" Global variables"""
key = 0
beautiful_chords = []
track_notes = []
tpb = 0
velocity = 0
st_key = 0
track_len = 0
f_note = ''

population = []


@dataclass
class Major:
    value = 0

@dataclass
class Minor:
    value = 1

@dataclass
class Dim:
    value = -1

""" Algebraic data type for main used chords"""
ChordType = Major | Minor | Dim

def get_accompaniment():
    """Returns consonant chords for the melody

    Returns:
        list((int, ChordType)): consonant chords for the melody
    """
    return zip([5, 7, 9, 2, 4, 11], [Major(), Major(), Minor(), Minor(), Minor(), Dim()])

""" Constants"""
def get_octaves_no():
    return 10

def get_keys_no():
    return 12

def get_generations_no():
    return 1000

def get_population_size():
    return 100

def get_total_keys_no():
    return get_keys_no() * get_octaves_no()

def get_shift(chord: ChordType):
    """Return shift for a chord with the given type

    Args:
        chord (ChordType): Type of the chord.

    Returns:
        list(int): Triad of notes that represent this chord.
    """
    match chord:
        case Major():
            return [0, 4, 7]
        case Minor():
            return [0, 3, 7]
        case Dim():
            return [0, 3, 6]

def set_key(file_name):
    """Initialize global variable key from music file

    Args:
        file_name (str): name of the music file
    """
    global key 
    key = parse_key(get_key(file_name), get_mode(file_name))

def init_beautiful_chords():
    """Initialize consonants"""
    global beautiful_chords
    beautiful_chords.append(get_chord_notes(0, Major()))
    beautiful_chords.extend(list(map(lambda c: get_chord_notes((key + c[0]) % 12, c[1]), get_accompaniment())))

def init_track_notes(midi_track):
    """Reads track notes from the music file

    Args:
        midi_track: track from the music file
    """
    length = get_length(midi_track)
    global track_notes
    track_notes = [None] * length
    total_time = 0
    for beat in filter(lambda c: type(c) == mido.Message, midi_track):
        total_time = set_note(beat, total_time)

def init_velocity(midi_track):
    """Reads velocity of the track

    Args:
        midi_track: track from the music file
    """
    global velocity
    vs = list(map(lambda c: c.velocity, filter(lambda c: type(c) == mido.Message and c.type == 'note_on', midi_track)))
    velocity = int(sum(vs) / len(vs) * 0.9)

def init_st_key(midi_track):
    """Computes the most valuable key in the music track

    Args:
        midi_track: track from the music file
    """
    global st_key
    os = list(map(lambda c: c.note // get_keys_no(), filter(lambda c: type(c) == mido.Message and c.type == 'note_on', midi_track)))
    st_key = get_keys_no() * int(sum(os) / len(os) - 1)

def init_population():
    """Generates random population"""
    global population
    population.extend([get_rand_chord() for _ in range(track_len)] for _ in range(get_population_size()))

def init_f_note(file_name):
    """Reads first note name from the music file

    Args:
        file_name (str): name of the file
    """
    global f_note
    f_note = music21.converter.parse(file_name).analyze('key').tonic.name
    if music21.converter.parse(file_name).analyze('key').mode == 'minor': f_note += '#m'

def get_chord_notes(starting_note, chord):
    """Returns a chord from the initial note and its type.

    Args:
        starting_note (int): First note of the chord.
        chord (Chord): Chord type(Major, Minor, or Dim)

    Returns:
        list[int]: list of notes in a chord
    """
    shift = get_shift(chord)
    first_note = (starting_note // 12) * 12
    return [first_note + (starting_note % 12 + mv) % 12 for mv in shift]


def get_rand_chord_type():
    """Generates random chord type

    Returns:
        ChordType: type of the chord
    """
    return random.choice([Major(), Minor(), Dim()])

def get_rand_chord():
    """Generates random chord

    Returns:
        list(int): triad of ints that represent random chord
    """
    return get_chord_notes(random.randint(0, get_total_keys_no()), get_rand_chord_type())

def parse_key(key, mode):
    """Parses the music key from the file

    Args:
        key (int): key from the file
        mode (str): major or minor mode

    Returns:
        int: key translated into the major
    """
    match mode:
        case 'major':
            return key % 12
        case 'minor':
            return (key + 3) % 12

def get_key(file_name):
    """Returns key from music file

    Args:
        file_name (str): file name

    Returns:
        int: music file key
    """
    return music21.converter.parse(file_name).analyze('key').tonic.midi

def get_mode(file_name):
    """Returns major or minor type of the music file

    Args:
        file_name (str): file name

    Returns:
        str: mode of the music file
    """
    return music21.converter.parse(file_name).analyze('key').mode

def mutate(track, mutation_no):
    """Make a mutation of melody

    Args:
        track (list(list(int))): melody represented by a sequence of triads
        mutation_no (int): Number of mutation on a cell
    """
    for _ in range(mutation_no):
        track[random.randint(0, len(track) - 1)] = get_rand_chord()

def cross(m1, m2):
    """Make a crossover on a given cell

    Args:
        m1 (list(list(int))): parent 1
        m2 (list(list(int))): parent 2

    Returns:
        list(list(int)): New melody
    """
    p = random.randint(0, len(m1[0]))
    return m1[:p] + m2[p:]


def check_consonant_chord(chord):
    """Checks whether given chord is consonant with the melody or not

    Args:
        chord (list(int)): triad that represent this chord

    Returns:
        bool: is consonant or not
    """
    return len(list(filter(lambda c: c == chord, beautiful_chords))) != 0

def calculate_fitness(track):
    """Calculate fitness value for a given melody

    Args:
        track (list(list(int))): melody

    Returns:
        int: fitness value
    """
    return len(list(filter(check_consonant_chord, track)))     * 70 + \
           len(list(filter(lambda c: c == None, track_notes))) * 2 + \
           len(list(filter(lambda n: n in track_notes, [note for chord in track for note in chord]))) * 3 # TODO: check

def get_length(midi_track):
    """Returns number of notes in melody

    Args:
        midi_track: music track

    Returns:
        int: number of notes
    """
    return (sum(list(map(lambda c: c.time, list(filter(lambda c: type(c) == mido.Message, midi_track))))) + tpb - 1) // tpb

def set_note(beat, total_time):
    """Reads note from the music file and initializes it

    Args:
        beat (int): note
        total_time (int): time when this note should be played

    Returns:
        int: new time
    """
    global track_notes
    match beat.type:
        case 'note_on':
            if total_time % tpb == 0 and track_notes[total_time // tpb] == None: track_notes[total_time // tpb] = beat.note
        case 'note_of':
            if track_notes[-1] == None: track_notes[-1] = beat.note
    return total_time + beat.time

def sift_population():
    """Chooses best melodies from the population and kills other ones"""
    global population
    population.sort(key=lambda m: calculate_fitness(m), reverse=True)
    population = population[:get_population_size()]

def update_population():
    """Adds new melodies taking the best ones experience"""
    for _ in range(get_population_size() // 2):
        parents = random.sample(range(0, len(population) // 2), 2)
        n = cross(population[parents[0]], population[parents[1]])
        mutate(n, random.randint(0, len(population) // 4))
        population.append(n)

def improve_population():
    """Main cycle of the GA - it trains the population"""
    for _ in range(get_generations_no()):
        update_population()
        sift_population()

def generate_accompaniment():
    """Reads file name from user and starts the algorithm"""
    input_name = input('Enter name of the file with the extension: ')
    print('Generating accompaniment. It may take a while...')
    number = input_name[-5]

    music = mido.MidiFile(input_name, clip=True)
    init_f_note(input_name)
    output = 'EvgenyGerasimovOutput' + number + '-' + f_note + '.mid'
    global tpb, track_len
    tpb = music.ticks_per_beat * 2
    init_track_notes(music.tracks[1])
    track_len = len(track_notes)
    set_key(input_name)
    init_beautiful_chords()
    init_st_key(music.tracks[1])
    init_velocity(music.tracks[1])
    init_population()
    
    improve_population()

    tempo=0
    for track in music.tracks:
        for msg in filter(lambda c: type(c) == mido.MetaMessage and c.type == 'set_tempo', track):
                tempo = msg.tempo

    # Start writing final track.
    accompaniment = population[0]
    tracks = [mido.MetaMessage('set_tempo', tempo=tempo, time=0)]
    
    for c in accompaniment:
        for n in c:
            tracks.append(mido.Message('note_on',channel=0,note=n%12+st_key,velocity=velocity,time=0))        
        tracks.append(mido.Message('note_off',channel=0,note=c[0]%12+st_key,velocity=velocity,time=tpb))
        for i in range(1, 2):
            tracks.append(mido.Message('note_off',channel=0,note=n%12+st_key,velocity=velocity,time=0))

    music.tracks.append(tracks)
    music.save(output)
    print('Done! File saved as ' + output)

generate_accompaniment()