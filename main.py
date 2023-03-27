import json
from flask import Flask, request, jsonify

# utility functions
from utils import data_to_json, read_to_create, write_to_file, id_checker

# constant
VOTERS_FILE = './data/voters.txt'
ELECTIONS_FILE = './data/elections.txt'
RESULTS_FILE = './data/results.txt'

app = Flask(__name__)


# -------------------- VOTER ROUTES ------------------

# registering a voter
@app.route('/voters', methods=['POST'])
def create_voter():
    
    new_voter = json.loads(request.data)
    voters_records, wasEmpty = read_to_create(VOTERS_FILE, new_voter)
    
    # checking if the user is new
    if not wasEmpty:
        for voter in voters_records:
            if voter['student_id'] == new_voter['student_id']:
                return jsonify({'ERROR': 'User Already Exists'}), 403
        
        voters_records.append(new_voter)
    write_to_file(VOTERS_FILE, voters_records)
    return jsonify(new_voter)

# retrieving registered voters
@app.route('/voters', methods=['GET'])
def retrieve_voters():

    try:
        voters_records = data_to_json(VOTERS_FILE) 
        return jsonify(voters_records)
    except:
        return jsonify({'ERROR': 'No Data Found'}), 404

# retrieeving a registered voter  
@app.route('/voters/<id>', methods=['GET'])
def retrieve_voter(id):

    voters_records = data_to_json(VOTERS_FILE)
    for voter in voters_records:
        if voter['student_id'] == id:
            return jsonify(voter), 200
    return jsonify({'ERROR': 'No Data Found'}), 404
        
# de-registering all registered voters
@app.route('/voters', methods=['DELETE'])
def delete_voters():

    return jsonify({'ERROR': 'Permission Denied'}), 403
    
# de-registering a registered voters
@app.route('/voters/<student_id>', methods=['DELETE'])
def delete_voter(student_id):

    if student_id == None: return jsonify({'ERROR': 'Permission Denied'}), 403
    deleted_voter = None
    new_voters_list = []

    voters_records = data_to_json(VOTERS_FILE)

    # deleting a record
    for voter_record in voters_records:
        if voter_record['student_id'] == student_id:
            deleted_voter = voter_record
            continue
        new_voters_list.append(voter_record)

    write_to_file(VOTERS_FILE, new_voters_list)

    if deleted_voter == None:
        return jsonify({'ERROR': 'Voter Not Found'}), 204
    return jsonify(deleted_voter), 202

# updating a registered voter
@app.route('/voters', methods=['PUT', 'PATCH'])
def update_voters():

    voter = json.loads(request.data)
    updated_voter = None
    new_voters_data = []
    records = data_to_json(VOTERS_FILE)
    
    # try updating
    for r in records:
        if r['student_id'] == voter['student_id']:
            for key in voter:
                r[key] = voter[key]
            updated_voter = r
        new_voters_data.append(r)

    # add voter if not in the file
    if updated_voter == None:
        new_voters_data.append(voter)

    write_to_file(VOTERS_FILE, new_voters_data)
    return jsonify(updated_voter), 201

    
# ------------------------ ELECTION ROUTE -------------------
# creating an election
@app.route('/elections', methods=['POST'])
def create_election():

    new_election = json.loads(request.data)

    response_election = new_election.copy()
    
    elections_records, wasEmpty = read_to_create(ELECTIONS_FILE, new_election)

    # recording the election data
    if not wasEmpty:

        for election in elections_records:
            if election['election_id'] == new_election['election_id']:
                return jsonify({'ERROR': 'Election Already Exists'}), 403   
        
        elections_records.append(new_election)

    # creating result for the election
    new_result = {}
    new_result['election_id'] = new_election['election_id']
    new_result['results'] = []

    for position in  new_election['candidates']:

        for role, candidates in position.items():
            new_result['results'].append({role:{}})
            role_index = new_result['results'].index({role:{}})
            for candidate in candidates:
                new_result['results'][role_index][role][candidate] = "0"
            new_result['results'][role_index][role]['voters'] = []

    results_records, wasEmpty = read_to_create(RESULTS_FILE, new_result)
    
    if not wasEmpty: results_records.append(new_result)

    # write to both files
    write_to_file(RESULTS_FILE, results_records)
    write_to_file(ELECTIONS_FILE, elections_records)
    
    return jsonify(response_election)


# retrieving an election data / all elections
@app.route('/elections', methods=['GET'])
def retrieve_elections():

    response_data = []
    
    results = data_to_json(RESULTS_FILE)
    elections_records = data_to_json(ELECTIONS_FILE)
    
    # combine data from results file and elections data
    for election in elections_records:
        response_entry = {}
        for res in results:
            if res['election_id'] == election['election_id']:
                response_entry['election_id'] = res['election_id']
                response_entry['election_name'] = election['election_name']
                response_entry['election_startdate'] = election['election_startdate']
                response_entry['election_enddate'] = election['election_enddate']
                response_entry['results'] = res['results']
        response_data.append(response_entry)
    
    # check if there is any data in the file
    if response_data == []:
        return jsonify({'ERROR': 'No Data Found'}), 404
    return jsonify(response_data)

#retrieve single election     
@app.route('/elections/<election_id>', methods=['GET'])
def retrieve_election(election_id):
    
    results = data_to_json(RESULTS_FILE)
    elections_records = data_to_json(ELECTIONS_FILE)

    # combine data from results and elections 
    for election in elections_records:
        if election['election_id'] == election_id:
            response_entry = {}
            for res in results:
                if res['election_id'] == election['election_id']:
                    response_entry['election_id'] = res['election_id']
                    response_entry['election_name'] = election['election_name']
                    response_entry['election_startdate'] = election['election_startdate']
                    response_entry['election_enddate'] = election['election_enddate']
                    response_entry['results'] = res['results']
                    return jsonify(response_entry)
                
    return jsonify({'ERROR': 'No Data Found'}), 404

# deleting all elections
@app.route('/elections', methods=['DELETE'])
def delete_elections():

    return jsonify({'ERROR': 'Permission Denied'}), 403

# delete a single election
@app.route('/elections/<election_id>', methods=['DELETE'])
def delete_election(election_id):

    if election_id == None: return jsonify({'ERROR': 'Permission Denied'}), 403

    deleted_election = None
    new_elections_list = []
    new_results = []

    results = data_to_json(RESULTS_FILE)
    
    # delete election results
    for result in results:
        if result['election_id'] == election_id:
            continue
        new_results.append(result)

    elections_records = data_to_json(ELECTIONS_FILE)

    # delete election in elections
    for election in elections_records:
        if election['election_id'] == election_id:
            deleted_election = election
            continue
        new_elections_list.append(election)

    # write to both files
    write_to_file(RESULTS_FILE, new_results)
    write_to_file(ELECTIONS_FILE, new_elections_list)
    
    if deleted_election == None:
        return jsonify({'ERROR': 'Election Not Found'}), 404
    return jsonify(deleted_election), 200


# voting in an election
@app.route('/elections/vote', methods=['POST'])
def voting():

    voting_details = json.loads(request.data)

    response_details = voting_details.copy()

    # check voting details
    if voting_details == None: return jsonify({'ERROR': 'Permission Denied'}), 403

    if not id_checker(VOTERS_FILE, voting_details['student_id'], 'student_id'):
        return jsonify({'ERROR': 'Voter Not Found, Please Register'}), 404
    
    if not id_checker(ELECTIONS_FILE, voting_details['election_id'], 'election_id'):
        return jsonify({'ERROR': 'Election Not Found'}), 404
    
    # collect the position the user has chosen to vote for
    chosen_candidates = {}
    elections_records = data_to_json(ELECTIONS_FILE)

    for election in elections_records:

        if election['election_id'] == voting_details["election_id"]:

            for key, value in voting_details.items():

                for position in election['candidates']:
                    if key in position:
                        chosen_candidates[key] = value
                        break
    
    # updating the results
    new_results = []
    
    results_records = data_to_json(RESULTS_FILE)
    for result in results_records:
        if result['election_id'] == voting_details['election_id']:
            for pos, candidate_name in chosen_candidates.items():
                
                for results_record in  result['results']:
                    
                    candidates_for_pos = results_record.get(pos)

                    # handle case when the person is voting for only one position
                    if candidates_for_pos == None:
                        continue

                    # check if the voter has not voted already
                    if voting_details['student_id'] in candidates_for_pos.get('voters'):
                        response_details[pos] = "Voted Already"
                    
                    else:
                        # check if candidate exists
                        if candidate_name not in candidates_for_pos:
                                response_details[pos] = f"{candidate_name} Not A Candidate For Position"
                                continue
                        
                        # increment the number of votes
                        candidates_for_pos[candidate_name] = int(candidates_for_pos.get(candidate_name)) + 1
                        
                        # add voter to the list of voters
                        candidates_for_pos.get('voters').append(voting_details['student_id'])
                                        
        new_results.append(result)
       
    # write the new results to the file
    write_to_file(RESULTS_FILE, new_results)
    return jsonify(response_details), 200

app.run(debug=True)