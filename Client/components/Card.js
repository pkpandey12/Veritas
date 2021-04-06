import React, { Component } from 'react';
import { Image, View, StyleSheet, Dimensions } from 'react-native';
import { Container, Header, Content, Card, CardItem, Thumbnail, Text, Button, Icon, Left, Body } from 'native-base';
import moment from 'moment';
const { height } = Dimensions.get('window');

const B = (props) => <Text style={{fontWeight: 'bold'}}>{props.children}</Text>

const styles = StyleSheet.create({
    font: {
        fontSize: 9
    }
})
//<Text>datetime: {datetime?datetime:""} </Text>
export default ({
    state, address, blockHash, transactionHash, label, createdAt, datetime
}) => (
        <View style={{ height: height / 6 }}>
            <Card style={{ flex: 1 }}>
                <CardItem>
                    <Left>
                        <Thumbnail square source={{ uri: address }} />
                        <Body>
                            <Text><B>Name: </B>{label} </Text>
                            <Text style={styles.font}><B>Date and Time: </B>{moment(createdAt).format("MMMM Do YYYY, h:mm:ss a")}</Text>
                            <Text style={styles.font}><B>Address:</B> {address}</Text>
                            <Text style={styles.font}> <B>BlockHash:</B> {blockHash}</Text>
                        </Body>
                    </Left>
                </CardItem>
            </Card>
        </View>
    )
