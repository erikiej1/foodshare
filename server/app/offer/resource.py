from flask_restful import Resource, abort
from flask import request, json
from app import ecv
import datetime
from models.offer import Offer
from models.user import User
from app.general_responses import *
from message_queue.publish import Publisher
# from app import publisher

class OfferListResource(Resource):

    def get(self):
        return [offer.to_dict() for offer in ecv.session.query(Offer).all()]

    def post(self):
        data = check_request_json(request)

        host_id = data.get('host_id')
        if host_id is None:
            missing_required_field('host_id')

        portions = data.get('portions')
        if portions is None:
            missing_required_field('portions')

        price = data.get('price')
        if price is None:
            missing_required_field('price')

        info = data.get('info')
        if info is None:
            missing_required_field('info')

        time_ready = data.get('time_ready')
        if time_ready is None:
            missing_required_field('time_ready')
            
        if ecv.testing:
            user = ecv.session.query(User).filter_by(id=host_id).first()
            offer = Offer(
                host=user, 
                portions=portions, 
                price=price, 
                info=info, 
                time_ready=datetime.datetime.fromtimestamp(time_ready))
            ecv.session.add(offer)
            ecv.session.commit()

            return offer.to_dict(), 201
        else:
            p = Publisher()
            result = p.addoffer(host_id=host_id,portions=portions,price=price,info=info,time_ready=time_ready)
            return result, 201

class OfferResource(Resource):
    def get(self, offer_id):
        offer = ecv.session.query(Offer).filter_by(id=offer_id).first()
        if not offer:
            abort(404, message='Offer with id {} does not exist.'.format(offer_id))
        return offer.to_dict()

    def put(self, offer_id):
        data = check_request_json(request)
        portions = data.get('portions')
        price = data.get('price')
        info = data.get('info')
        time_ready = data.get('time_ready')

        p = Publisher()
        result = p.updateoffer(offer_id=offer_id, portions=portions, price=price, info=info, time_ready=time_ready)
        return result, 201

    def delete(self, offer_id):
        if ecv.testing:
            offer = ecv.session.query(Offer).filter_by(id=offer_id).first()
            if not offer:
                abort(404, message='Offer with id {} does not exist.'.format(offer_id))
            ecv.session.delete(offer)
            ecv.session.commit()
            result = dict()
        else:
            p = Publisher()
            result = p.deleteoffer(offer_id=offer_id)
        return result, 200
        
