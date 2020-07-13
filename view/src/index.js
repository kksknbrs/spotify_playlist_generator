import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Form from 'react-bootstrap/Form';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';

// artist nameとtrack nameの入力/出力蘭。一曲分。
class List extends React.Component {
  render() {
    return (
      <Container>
        <Row>
          <Col xs={1}>{this.props.rowNum}</Col>
          <Col>
          {/* artist name */}
            <Form.Control 
              type="text" 
              value={this.props.artistName}
              onChange={(e) => this.props.onChange_artist(this.props.rowNum-1, e.target.value)}
            />
          </Col>
          <Col>
          {/* track name */}
            <Form.Control 
              type="text"
              value={this.props.trackName}
              onChange={(e) => this.props.onChange_track(this.props.rowNum-1, e.target.value)}
            />
          </Col>
          <Col>
          {/* Search button */}
            <Button 
              variant="primary" 
              type="button"  
              onClick={() => this.props.onClick_button(this.props.rowNum-1)}
              size="sm">
                Search
            </Button>
          </Col>
        </Row>
      </Container>
    )
  }
}

// 全曲分のartist name
class ListsContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      artistNames: Array(this.props.n_row),
      trackNames: Array(this.props.n_row),
    };
  }

  handleArtistName(rowNum, newArtistName) {
    const newArtistNames = this.state.artistNames;
    newArtistNames[rowNum] = newArtistName;

    this.setState({
      artistName: newArtistName,
    });
  }

  handleTrackName(rowNum, newTrackName) {
    const newTrackNames = this.state.trackNames
    newTrackNames[rowNum] = newTrackName;

    this.setState({
      trackNames: newTrackNames,
    });
  }

  handleButton(rowNum) {
    const artistName = this.state.artistNames[rowNum];
    const trackName = this.state.trackNames[rowNum];
    if (artistName || trackName) {
      // 両方が空欄である時は検索させない
      const request = new XMLHttpRequest();
      const URL = "http://127.0.0.1:5000/search?"
                  + "artist="
                  + artistName
                  + "&track="
                  + trackName;

      request.open('GET', URL, true);
      request.onload = function() {
        const data = this.response;
        console.log(data)
      };
      request.send();
    }
  }

  render() {
    const n_row = this.props.n_row;
    const lists = Array.from(Array(n_row), (v,i) => {
      return (
        <List 
          key={i}
          rowNum={i+1}
          artistName={this.state.artistNames[i]}
          onChange_artist={this.handleArtistName.bind(this)}
          onChange_track={this.handleTrackName.bind(this)}
          onClick_button={this.handleButton.bind(this)}
        />
      )
    });

    return (
      <div>
        <Form>
          <Form.Label>Result</Form.Label>
          <Container>
            <Row>
              <Col xs={1}></Col>
              <Col>Artist Name</Col>
              <Col>Track Name</Col>
              <Col></Col>
            </Row>
          </Container>
          {lists}
        </Form>
      </div>
    )
  }
}

ReactDOM.render(
  <ListsContainer n_row={10} />,
  document.getElementById("root")
);

