import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Form from 'react-bootstrap/Form';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

// artist nameとtrack nameの入力/出力蘭。一曲分。
class List extends React.Component {
  render() {
    return (
      <Container>
        <Row>
          <Col xs={1}>{this.props.rowNum}</Col>
          <Col>
            <Form.Control 
              type="text" 
              value={this.props.artistName}
              onChange={(e) => this.props.onChange(this.props.rowNum-1, e.target.value)}
            />
          </Col>
          <Col><Form.Control type="text" /></Col>
        </Row>
      </Container>
    )
  }
}

// 全曲分のartist name、
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

  render() {
    const n_row = this.props.n_row;
    const lists = Array.from(Array(n_row), (v,i) => {
      return (
        <List 
          key={i}
          rowNum={i+1}
          artistName={this.state.artistNames[i]}
          onChange={this.handleArtistName.bind(this)}
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

